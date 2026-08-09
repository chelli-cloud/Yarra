import csv

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.conf import settings
import razorpay

from tenants.models import Profile, School, Notification
from tenants.notifications import create_notification, log_activity
from tenants.utils import generate_invoice_pdf, generate_certificate_pdf
from .models import Event, EventCategory, StudentRegistration, PaymentStatus, CompetitionResult, EventPhoto


# Permission constants following existing tenants pattern
SL_ANALYTICS_ROLES = ['school_leader']


STAFF_ROLES = ['admin', 'school_leader', 'teacher', 'pl_teacher']


def _get_user_profile(request):
    """Get the user's profile for role checking."""
    if not request.user.is_authenticated:
        return None
    return Profile.objects.filter(user=request.user).first()


def _is_school_staff(profile):
    return bool(profile and profile.role in STAFF_ROLES)


@login_required
def event_list(request):
    """Browse all active Yarra events, excluding opportunities."""
    profile = _get_user_profile(request)
    if not profile and not request.user.is_superuser:
        messages.error(request, "Please complete your profile to access events.")
        return redirect('school_profile')

    category = request.GET.get('category')

    # Events are Yarra-wide: every school sees every active event.
    events = Event.objects.filter(is_active=True).exclude(category=EventCategory.OPPORTUNITY)

    if category:
        events = events.filter(category=category)

    events = events.select_related('school', 'created_by')

    # Remove OPPORTUNITY from category choices for filtering in the main list
    comp_categories = [c for c in EventCategory.choices if c[0] != EventCategory.OPPORTUNITY]

    context = {
        'events': events,
        'categories': comp_categories,
        'current_category': category,
        'can_create_event': request.user.is_superuser,
        'profile': profile,
    }
    return render(request, 'competitions/event_list.html', context)


@login_required
def event_detail(request, pk):
    """View event details, download brochure, see payment info."""
    profile = _get_user_profile(request)
    if not profile and not request.user.is_superuser:
        messages.error(request, "Please complete your profile.")
        return redirect('school_profile')

    # Events are Yarra-wide: any authenticated user can view any event's details.
    event = get_object_or_404(
        Event.objects.select_related('school', 'created_by').prefetch_related('results', 'registrations'),
        pk=pk
    )

    context = {
        'event': event,
        'profile': profile,
        'can_edit': request.user.is_superuser,
        'can_manage_participants': request.user.is_superuser or _is_school_staff(profile),
    }
    return render(request, 'competitions/event_detail.html', context)


@login_required
def event_participants(request, pk):
    """Participant Records for a concluded event: registrations grouped by school.
    Reached from the Events tab, per Chelli's request to move this off the dashboard."""
    profile = _get_user_profile(request)
    event = get_object_or_404(Event.objects.select_related('school'), pk=pk)

    # Events are Yarra-wide now: any staff role (or Super Admin) can view participant records,
    # not just staff from the event's original school.
    if not (request.user.is_superuser or _is_school_staff(profile)):
        messages.error(request, "You don't have permission to view participant records for this event.")
        return redirect('event_list')

    registrations = StudentRegistration.objects.filter(event=event).select_related('school')
    by_school = registrations.values('school__name').annotate(count=Count('id')).order_by('-count')

    context = {
        'event': event,
        'registrations': registrations,
        'by_school': by_school,
        'total_participants': registrations.count(),
    }
    return render(request, 'competitions/event_participants.html', context)


@login_required
def export_participants_csv(request, pk):
    """M6: CSV export of an event's attendee list."""
    profile = _get_user_profile(request)
    event = get_object_or_404(Event, pk=pk)

    if not (request.user.is_superuser or _is_school_staff(profile)):
        messages.error(request, "You don't have permission to export participant records for this event.")
        return redirect('event_list')

    registrations = StudentRegistration.objects.filter(event=event).select_related('school')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{event.title}_attendees.csv"'
    writer = csv.writer(response)
    writer.writerow(['Participant', 'School', 'Payment Status', 'Attended', 'Registered At'])
    for reg in registrations:
        writer.writerow([
            reg.display_name,
            reg.school.name if reg.school else '',
            reg.get_payment_status_display(), reg.attended,
            reg.registered_at.strftime('%Y-%m-%d %H:%M'),
        ])
    return response


@login_required
def event_create(request):
    """Create a new Yarra event (Super Admin only)."""
    if not request.user.is_superuser:
        messages.error(request, "You don't have permission to create events.")
        return redirect('event_list')

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        category = request.POST.get('category')
        registration_link = request.POST.get('registration_link')
        razorpay_payment_link = request.POST.get('razorpay_payment_link', '')
        fee_type = request.POST.get('fee_type', Event.FeeType.PAID)
        fee = 0.00 if fee_type == Event.FeeType.PRO_BONO else request.POST.get('fee', 0.00)

        event = Event.objects.create(
            created_by=request.user,
            title=title,
            description=description,
            category=category,
            registration_link=registration_link,
            razorpay_payment_link=razorpay_payment_link,
            fee_type=fee_type,
            fee=fee,
        )

        # Handle file uploads
        if request.FILES.get('brochure'):
            event.brochure = request.FILES['brochure']
        if request.FILES.get('payment_qr'):
            event.payment_qr = request.FILES['payment_qr']

        event.save()
        log_activity(request.user, f"Created event '{title}'", target_url=event.get_absolute_url())
        messages.success(request, f"Event '{title}' created successfully!")
        return redirect('event_detail', pk=event.pk)

    context = {
        'categories': [c for c in EventCategory.choices if c[0] != EventCategory.OPPORTUNITY],
        'mode': 'create',
    }
    return render(request, 'competitions/event_form.html', context)


@login_required
def event_edit(request, pk):
    """Edit an existing event (Super Admin only)."""
    event = get_object_or_404(Event, pk=pk)

    if not request.user.is_superuser:
        messages.error(request, "You don't have permission to edit this event.")
        return redirect('event_detail', pk=event.pk)

    if request.method == 'POST':
        event.title = request.POST.get('title', event.title)
        event.description = request.POST.get('description', event.description)
        event.category = request.POST.get('category', event.category)
        event.registration_link = request.POST.get('registration_link', event.registration_link)
        event.razorpay_payment_link = request.POST.get('razorpay_payment_link', event.razorpay_payment_link)
        event.winners = request.POST.get('winners', event.winners)
        event.is_active = request.POST.get('is_active') == 'on'
        event.fee_type = request.POST.get('fee_type', event.fee_type)
        event.fee = 0.00 if event.fee_type == Event.FeeType.PRO_BONO else request.POST.get('fee', event.fee)
        event.recording_url = request.POST.get('recording_url', event.recording_url)

        # Handle file uploads
        if request.FILES.get('brochure'):
            event.brochure = request.FILES['brochure']
        if request.FILES.get('payment_qr'):
            event.payment_qr = request.FILES['payment_qr']
        if request.FILES.get('winning_resources'):
            event.winning_resources = request.FILES['winning_resources']
        if request.FILES.get('presentation_file'):
            event.presentation_file = request.FILES['presentation_file']

        event.save()

        for photo in request.FILES.getlist('event_photos'):
            EventPhoto.objects.create(event=event, image=photo)

        messages.success(request, f"Event '{event.title}' updated successfully!")
        return redirect('event_detail', pk=event.pk)

    context = {
        'event': event,
        'categories': [c for c in EventCategory.choices if c[0] != EventCategory.OPPORTUNITY],
        'mode': 'edit',
    }
    return render(request, 'competitions/event_form.html', context)


@login_required
@require_POST
def event_delete(request, pk):
    """Delete an event (Super Admin only). Registrations and results cascade-delete with it."""
    if not request.user.is_superuser:
        messages.error(request, "You don't have permission to delete events.")
        return redirect('event_detail', pk=pk)

    event = get_object_or_404(Event, pk=pk)
    title = event.title
    event.delete()
    log_activity(request.user, f"Deleted event '{title}'")
    messages.success(request, f"Event '{title}' and all its registrations/results have been deleted.")
    return redirect('event_list')


@login_required
def register_for_event(request, pk):
    """School Admin/Teacher registers a participant (by name) for an event on the school's behalf."""
    profile = _get_user_profile(request)
    if not (request.user.is_superuser or _is_school_staff(profile)):
        messages.error(request, "You don't have permission to register participants for events.")
        return redirect('event_list')

    event = get_object_or_404(Event, pk=pk, is_active=True)

    if request.method != 'POST':
        return redirect('event_detail', pk=event.pk)

    participant_name = request.POST.get('participant_name', '').strip()
    if not participant_name:
        messages.error(request, "Please provide the participant's name.")
        return redirect('event_detail', pk=event.pk)

    school = profile.school if profile else None
    if request.user.is_superuser and request.POST.get('school'):
        school = School.objects.filter(pk=request.POST.get('school')).first() or school

    registration = StudentRegistration.objects.create(
        event=event,
        school=school,
        participant_name=participant_name,
        registered_by=request.user,
        payment_screenshot=request.FILES.get('payment_screenshot'),
    )

    if event.created_by:
        create_notification(
            recipient=event.created_by,
            title='New event registration',
            message=f"{participant_name} was registered for {event.title} by {request.user.username}.",
            level='info',
            target_url=event.get_absolute_url() if hasattr(event, 'get_absolute_url') else f"/competitions/{event.pk}/",
            data={'registration_id': registration.pk},
        )
    log_activity(request.user, f"Registered '{participant_name}' for event '{event.title}'", school=school, target_url=event.get_absolute_url())

    fee_in_paise = int(event.fee * 100) # Use event's specific fee
    if settings.RAZORPAY_KEY_ID and settings.RAZORPAY_SECRET:
        try:
            client = razorpay.Client(
                auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET)
            )
            order_data = client.order.create({
                'amount': fee_in_paise,
                'currency': 'INR',
                'payment_capture': 1
            })

            registration.razorpay_order_id = order_data.get('id', '')
            registration.save(update_fields=['razorpay_order_id', 'payment_status'])

            context = {
                'event': event,
                'registration': registration,
                'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                'order_id': order_data.get('id', ''),
                'amount': order_data.get('amount', 0),
                'amount_rupees': event.fee, # Use event's specific fee
            }
            return render(request, 'competitions/payment_checkout.html', context)

        except Exception as e:
            registration.payment_status = PaymentStatus.FAILED
            registration.save(update_fields=['payment_status'])
            messages.error(request, f"Razorpay initialization failed: {str(e)}. Please contact support or upload payment proof.")
            return redirect('event_detail', pk=event.pk)

    # Fallback to manual verification if Razorpay is not configured
    messages.warning(
        request,
        "Registration captured, but online payment via Razorpay is currently unavailable. "
        "Please ensure you have uploaded a payment screenshot for manual verification."
    )
    return redirect('registration_confirm', pk=event.pk)


@require_POST
@login_required
def verify_payment(request):
    """Verify Razorpay payment signature and update registration."""
    razorpay_payment_id = request.POST.get('razorpay_payment_id')
    razorpay_signature = request.POST.get('razorpay_signature')
    razorpay_order_id = request.POST.get('razorpay_order_id')
    registration = StudentRegistration.objects.filter(
        razorpay_order_id=razorpay_order_id,
        registered_by=request.user
    ).first()

    if not registration:
        return JsonResponse({'status': 'error', 'message': 'Registration not found'}, status=404)

    try:
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET)
        )
        client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        })

        registration.razorpay_payment_id = razorpay_payment_id
        registration.razorpay_signature = razorpay_signature
        registration.payment_status = PaymentStatus.VERIFIED
        registration.save()

        if registration.event.created_by:
            create_notification(
                recipient=registration.event.created_by,
                title='Payment verified',
                message=f"Payment for {registration.display_name}'s registration to {registration.event.title} was verified.",
                level='success',
                target_url=f"/competitions/{registration.event.pk}/",
                data={'registration_id': registration.pk},
            )
        log_activity(request.user, f"Payment verified for event '{registration.event.title}'", school=registration.event.school)

        return JsonResponse({'status': 'success', 'redirect_url': reverse('registration_confirm', args=[registration.event.pk])})
    except razorpay.errors.SignatureVerificationError:
        registration.payment_status = PaymentStatus.FAILED
        registration.save(update_fields=['payment_status'])
        return JsonResponse({'status': 'error', 'message': 'Payment verification failed'}, status=400)
    except Exception as exc:
        registration.payment_status = PaymentStatus.FAILED
        registration.save(update_fields=['payment_status'])
        return JsonResponse({'status': 'error', 'message': str(exc)}, status=400)


@login_required
def sl_analytics(request):
    """School Leader dashboard with competition analytics."""
    profile = _get_user_profile(request)
    if not profile or profile.role not in SL_ANALYTICS_ROLES:
        messages.error(request, "You don't have permission to view analytics.")
        return redirect('event_list')

    school = profile.school

    # Events are Yarra-wide now, so "school analytics" means this school's own participation
    # in Yarra events, not events the school owns.
    school_registrations = StudentRegistration.objects.filter(school=school)

    events_participated = Event.objects.filter(registrations__in=school_registrations).distinct()
    total_events = events_participated.count()
    active_events = events_participated.filter(is_active=True).count()
    total_registrations = school_registrations.count()
    verified_registrations = school_registrations.filter(payment_status=PaymentStatus.VERIFIED).count()
    pending_registrations = school_registrations.filter(payment_status=PaymentStatus.PENDING).count()
    total_prizes = CompetitionResult.objects.filter(school=school).count()

    # Events by category (this school's participation, by category)
    events_by_category = events_participated.values('category').annotate(count=Count('id'))

    # Recent results
    recent_results = CompetitionResult.objects.filter(
        school=school
    ).select_related('event')[:10]

    context = {
        'school': school,
        'total_events': total_events,
        'active_events': active_events,
        'total_registrations': total_registrations,
        'verified_registrations': verified_registrations,
        'pending_registrations': pending_registrations,
        'total_prizes': total_prizes,
        'events_by_category': list(events_by_category),
        'recent_results': recent_results,
    }
    return render(request, 'competitions/sl_analytics.html', context)


@login_required
def create_competition_result(request, event_pk):
    """Add a competition result for your own school's student (staff roles or Super Admin)."""
    profile = _get_user_profile(request)
    event = get_object_or_404(Event, pk=event_pk)

    if not (request.user.is_superuser or _is_school_staff(profile)):
        messages.error(request, "You don't have permission to add results.")
        return redirect('event_detail', pk=event.pk)

    if request.method == 'POST':
        student_name = request.POST.get('student_name')
        prize = request.POST.get('prize')
        # Superusers may specify a school explicitly; staff always report for their own school.
        school = profile.school if profile else None
        if request.user.is_superuser:
            school = School.objects.filter(pk=request.POST.get('school')).first() or school

        if student_name and prize and school:
            CompetitionResult.objects.create(
                event=event,
                school=school,
                student_name=student_name,
                prize=prize,
            )
            messages.success(request, f"Result added: {student_name} - {prize}")
        elif not school:
            messages.error(request, "Could not determine which school this result belongs to.")

    return redirect('event_detail', pk=event.pk)


def _can_manage_registration(request, registration):
    profile = _get_user_profile(request)
    return request.user.is_superuser or (
        _is_school_staff(profile) and profile.school_id == registration.school_id
    )


@login_required
def registration_confirm(request, pk):
    event = get_object_or_404(Event, pk=pk)
    registration = get_object_or_404(StudentRegistration, event=event, registered_by=request.user)
    if not _can_manage_registration(request, registration):
        messages.error(request, "You don't have permission to view this registration.")
        return redirect('event_list')
    return render(request, 'competitions/registration_confirm.html', {
        'event': event,
        'registration': registration,
    })


@login_required
def download_invoice(request, pk):
    """View to download the PDF invoice for a registration (staff of the registering school, or Super Admin)."""
    registration = get_object_or_404(StudentRegistration, pk=pk)
    if not _can_manage_registration(request, registration):
        messages.error(request, "You don't have permission to download this invoice.")
        return redirect('event_detail', pk=registration.event.pk)
    if registration.payment_status != PaymentStatus.VERIFIED:
        messages.error(request, "Invoice is only available for verified payments.")
        return redirect('event_detail', pk=registration.event.pk)

    pdf_buffer = generate_invoice_pdf(registration)
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_{registration.id}.pdf"'
    return response


@login_required
def download_certificate(request, pk):
    """M6: Download a PDF attendance certificate, once the participant has attended the event."""
    registration = get_object_or_404(StudentRegistration, pk=pk)
    if not _can_manage_registration(request, registration):
        messages.error(request, "You don't have permission to download this certificate.")
        return redirect('event_detail', pk=registration.event.pk)
    if not registration.attended:
        messages.error(request, "A certificate is only available after the participant has attended the event.")
        return redirect('event_detail', pk=registration.event.pk)

    if not registration.certificate_issued:
        registration.certificate_issued = True
        registration.save(update_fields=['certificate_issued'])

    pdf_buffer = generate_certificate_pdf(registration)
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Certificate_{registration.id}.pdf"'
    return response


@login_required
def mark_attendance(request, pk):
    """M6: Mark a participant as attended (staff can only mark their own school's participants)."""
    registration = get_object_or_404(StudentRegistration, pk=pk)

    if not _can_manage_registration(request, registration):
        messages.error(request, "You don't have permission to mark attendance.")
        return redirect('event_detail', pk=registration.event.pk)

    registration.attended = not registration.attended
    registration.save()

    status = "attended" if registration.attended else "not attended"
    messages.success(request, f"Marked {registration.display_name} as {status}.")
    return redirect('event_detail', pk=registration.event.pk)

@login_required
def submit_feedback(request, pk):
    """M6: Staff records feedback for a participant's event experience."""
    registration = get_object_or_404(StudentRegistration, pk=pk)
    if not _can_manage_registration(request, registration):
        messages.error(request, "You don't have permission to record feedback for this registration.")
        return redirect('event_detail', pk=registration.event.pk)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        text = request.POST.get('text', '')

        if rating:
            registration.feedback_rating = int(rating)
            registration.feedback_text = text
            registration.save()
            messages.success(request, "Thank you for your feedback!")
        else:
            messages.error(request, "Please provide a rating.")
            
    return redirect('event_detail', pk=registration.event.pk)

@login_required
@require_POST
def mark_notifications_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return redirect(request.POST.get('next') or 'school_profile')

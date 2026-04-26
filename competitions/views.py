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
from tenants.notifications import create_notification
from tenants.utils import generate_invoice_pdf
from .models import Event, EventCategory, StudentRegistration, PaymentStatus, CompetitionResult


# Permission constants following existing tenants pattern
EVENT_CREATE_ROLES = ['admin', 'teacher', 'school_leader']
EVENT_EDIT_ROLES = ['admin', 'teacher', 'school_leader']
SL_ANALYTICS_ROLES = ['school_leader']


def _get_user_profile(request):
    """Get the user's profile for role checking."""
    if not request.user.is_authenticated:
        return None
    return Profile.objects.filter(user=request.user).first()


def _can_create_event(profile):
    return profile and profile.role in EVENT_CREATE_ROLES


def _can_edit_event(profile, event, user):
    if not profile or profile.role not in EVENT_EDIT_ROLES:
        return False
    # Users can only edit events from their own school
    if profile.school_id != event.school_id:
        return False
    if profile.role in ['admin', 'school_leader']:
        return True
    return event.created_by == user


@login_required
def event_list(request):
    """Browse all active events, excluding opportunities."""
    profile = _get_user_profile(request)
    if not profile:
        messages.error(request, "Please complete your profile to access events.")
        return redirect('school_profile')

    category = request.GET.get('category')
    
    # Exclude 'OPPORTUNITY' for the main competitions list
    events = Event.objects.filter(is_active=True, school=profile.school).exclude(category=EventCategory.OPPORTUNITY)

    if category:
        events = events.filter(category=category)

    events = events.select_related('school', 'created_by')

    # Remove OPPORTUNITY from category choices for filtering in the main list
    comp_categories = [c for c in EventCategory.choices if c[0] != EventCategory.OPPORTUNITY]

    context = {
        'events': events,
        'categories': comp_categories,
        'current_category': category,
        'can_create_event': _can_create_event(profile),
        'profile': profile,
    }
    return render(request, 'competitions/event_list.html', context)


@login_required
def opportunity_list(request):
    """Browse all active opportunities for the school."""
    profile = _get_user_profile(request)
    if not profile:
        messages.error(request, "Please complete your profile.")
        return redirect('school_profile')

    # Only show 'OPPORTUNITY' category
    events = Event.objects.filter(
        is_active=True, 
        school=profile.school, 
        category=EventCategory.OPPORTUNITY
    ).select_related('school', 'created_by')

    context = {
        'events': events,
        'profile': profile,
        'can_create_event': _can_create_event(profile),
        'is_opportunity_view': True,
    }
    return render(request, 'competitions/opportunity_list.html', context)


@login_required
def event_detail(request, pk):
    """View event details, download brochure, see payment info."""
    profile = _get_user_profile(request)
    if not profile:
        messages.error(request, "Please complete your profile.")
        return redirect('school_profile')

    # Users can only view details of events from their own school
    event = get_object_or_404(
        Event.objects.filter(school=profile.school).select_related('school', 'created_by').prefetch_related('results', 'registrations'),
        pk=pk
    )

    registration = None
    if profile.role == 'student':
        registration = StudentRegistration.objects.filter(
            event=event, student=request.user
        ).first()

    context = {
        'event': event,
        'registration': registration,
        'profile': profile,
        'can_edit': _can_edit_event(profile, event, request.user),
    }
    return render(request, 'competitions/event_detail.html', context)


@login_required
def event_create(request):
    """Create a new event (Teachers, Admins, School Leaders only)."""
    profile = _get_user_profile(request)
    if not _can_create_event(profile):
        messages.error(request, "You don't have permission to create events.")
        return redirect('event_list')

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        category = request.POST.get('category')
        registration_link = request.POST.get('registration_link')
        razorpay_payment_link = request.POST.get('razorpay_payment_link', '')

        event = Event.objects.create(
            school=profile.school,
            created_by=request.user,
            title=title,
            description=description,
            category=category,
            registration_link=registration_link,
            razorpay_payment_link=razorpay_payment_link,
        )

        # Handle file uploads
        if request.FILES.get('brochure'):
            event.brochure = request.FILES['brochure']
        if request.FILES.get('payment_qr'):
            event.payment_qr = request.FILES['payment_qr']

        event.save()
        messages.success(request, f"Event '{title}' created successfully!")
        return redirect('event_detail', pk=event.pk)

    context = {
        'categories': EventCategory.choices,
        'mode': 'create',
    }
    return render(request, 'competitions/event_form.html', context)


@login_required
def event_edit(request, pk):
    """Edit an existing event (creator, Admins only)."""
    profile = _get_user_profile(request)
    event = get_object_or_404(Event, pk=pk)

    if not _can_edit_event(profile, event, request.user):
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

        # Handle file uploads
        if request.FILES.get('brochure'):
            event.brochure = request.FILES['brochure']
        if request.FILES.get('payment_qr'):
            event.payment_qr = request.FILES['payment_qr']
        if request.FILES.get('winning_resources'):
            event.winning_resources = request.FILES['winning_resources']

        event.save()
        messages.success(request, f"Event '{event.title}' updated successfully!")
        return redirect('event_detail', pk=event.pk)

    context = {
        'event': event,
        'categories': EventCategory.choices,
        'mode': 'edit',
    }
    return render(request, 'competitions/event_form.html', context)


@login_required
def register_for_event(request, pk):
    """Handle student registration after Google Form submission."""
    profile = _get_user_profile(request)
    if not profile or profile.role != 'student':
        messages.error(request, "Only students can register for events.")
        return redirect('event_list')

    event = get_object_or_404(Event, pk=pk, is_active=True)
    if profile.school_id != event.school_id:
        messages.error(request, "Students can only register for their own school's events.")
        return redirect('event_detail', pk=event.pk)

    existing = StudentRegistration.objects.filter(event=event, student=request.user).first()
    if existing:
        messages.info(request, "You are already registered for this event.")
        return redirect('event_detail', pk=event.pk)

    if request.method != 'POST':
        return redirect('event_detail', pk=event.pk)

    registration = StudentRegistration.objects.create(
        event=event,
        student=request.user,
        payment_screenshot=request.FILES.get('payment_screenshot'),
    )

    if event.created_by:
        create_notification(
            recipient=event.created_by,
            title='New event registration',
            message=f"{request.user.username} submitted registration for {event.title}.",
            level='info',
            target_url=event.get_absolute_url() if hasattr(event, 'get_absolute_url') else f"/competitions/{event.pk}/",
            data={'registration_id': registration.pk},
        )

    fee_in_paise = settings.COMPETITION_REGISTRATION_FEE * 100
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
                'amount_rupees': settings.COMPETITION_REGISTRATION_FEE,
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
        student=request.user
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
                message=f"{registration.student.username} completed payment for {registration.event.title}.",
                level='success',
                target_url=f"/competitions/{registration.event.pk}/",
                data={'registration_id': registration.pk},
            )

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

    # Analytics queries
    total_events = Event.objects.filter(school=school).count()
    active_events = Event.objects.filter(school=school, is_active=True).count()
    total_registrations = StudentRegistration.objects.filter(event__school=school).count()
    verified_registrations = StudentRegistration.objects.filter(
        event__school=school, payment_status=PaymentStatus.VERIFIED
    ).count()
    pending_registrations = StudentRegistration.objects.filter(
        event__school=school, payment_status=PaymentStatus.PENDING
    ).count()
    total_prizes = CompetitionResult.objects.filter(school=school).count()

    # Events by category
    events_by_category = Event.objects.filter(school=school).values('category').annotate(
        count=Count('id')
    )

    # Recent results
    recent_results = CompetitionResult.objects.filter(
        school=school
    ).select_related('event')[:10]

    # Teacher participation (who created events)
    teacher_participation = Event.objects.filter(
        school=school, created_by__isnull=False
    ).values('created_by__username').annotate(
        events_created=Count('id')
    ).order_by('-events_created')[:5]

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
        'teacher_participation': teacher_participation,
    }
    return render(request, 'competitions/sl_analytics.html', context)


@login_required
def create_competition_result(request, event_pk):
    """Add a competition result (winner/finalist announcement)."""
    profile = _get_user_profile(request)
    event = get_object_or_404(Event, pk=event_pk)

    if not _can_edit_event(profile, event, request.user):
        messages.error(request, "You don't have permission to add results.")
        return redirect('event_detail', pk=event.pk)

    if request.method == 'POST':
        student_name = request.POST.get('student_name')
        prize = request.POST.get('prize')

        if student_name and prize:
            # Result can only be added for the event's school (which is the user's school)
            CompetitionResult.objects.create(
                event=event,
                school=event.school,
                student_name=student_name,
                prize=prize,
            )
            messages.success(request, f"Result added: {student_name} - {prize}")

    return redirect('event_detail', pk=event.pk)


@login_required
def registration_confirm(request, pk):
    profile = _get_user_profile(request)
    if not profile or profile.role != 'student':
        messages.error(request, "Only students can view registration confirmations.")
        return redirect('event_list')

    event = get_object_or_404(Event, pk=pk)
    registration = get_object_or_404(StudentRegistration, event=event, student=request.user)
    return render(request, 'competitions/registration_confirm.html', {
        'event': event,
        'registration': registration,
    })


@login_required
def download_invoice(request, pk):
    """View to download the PDF invoice for a registration."""
    registration = get_object_or_404(StudentRegistration, pk=pk, student=request.user)
    if registration.payment_status != PaymentStatus.VERIFIED:
        messages.error(request, "Invoice is only available for verified payments.")
        return redirect('event_detail', pk=registration.event.pk)
    
    pdf_buffer = generate_invoice_pdf(registration)
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_{registration.id}.pdf"'
    return response


@login_required
@require_POST
def mark_notifications_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return redirect(request.POST.get('next') or 'school_profile')

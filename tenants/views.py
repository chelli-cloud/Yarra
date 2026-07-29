from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
from django.db.models import Count
from .models import (
    School, Profile, ReviewCycle, DiscussionThread, ThreadReply,
    Notification, Invitation, SchoolProfileExtended, SchoolDocument, Payment, ActivityLog,
)
from .forms import (
    InvitationForm, SchoolRegistrationForm, UserRegistrationForm,
    SchoolCreateForm, SchoolProfileExtendedForm, PaymentForm,
)
from .notifications import log_activity
import secrets

REVIEW_STATUS_DISPLAY = {
    'not_started': 'Not Started',
    'in_progress': 'In Progress',
    'completed': 'Completed',
}

PROFILE_EDIT_ROLES = ['school_leader', 'admin']
REVIEW_CYCLE_CREATE_ROLES = ['school_leader', 'admin']
REVIEW_EDIT_ROLES = ['school_leader', 'admin', 'pl_teacher']
LEADERSHIP_ROLES = ['school_leader', 'admin']
MAX_ADMINS_PER_SCHOOL = 2
MAX_TEACHERS_PER_SCHOOL = 5

@login_required
def my_profile(request):
    """Module: My Profile - personal details management."""
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        if request.user.is_superuser:
            return redirect('/admin/tenants/profile/add/')
        return render(request, 'tenants/access_denied.html', {'message': 'Profile missing.'})
    
    if request.method == 'POST':
        profile.date_of_birth = request.POST.get('date_of_birth') or None
        profile.mobile_no = request.POST.get('mobile_no', '')
        profile.alternate_mobile_no = request.POST.get('alternate_mobile_no', '')
        profile.emergency_contact_no = request.POST.get('emergency_contact_no', '')
        profile.gender = request.POST.get('gender', '')
        profile.blood_group = request.POST.get('blood_group', '')
        profile.nationality = request.POST.get('nationality', 'Indian')
        profile.religion = request.POST.get('religion', '')
        profile.category = request.POST.get('category', '')
        profile.aadhaar_no = request.POST.get('aadhaar_no', '')
        profile.pan_no = request.POST.get('pan_no', '')
        profile.languages_known = request.POST.get('languages_known', '')
        profile.extra_curricular = request.POST.get('extra_curricular', '')
        profile.permanent_address = request.POST.get('permanent_address', '')
        profile.current_address = request.POST.get('current_address', '')
        
        # Academic details (only updated if student)
        if profile.role == 'student':
            profile.grade = request.POST.get('grade', '')
            profile.section = request.POST.get('section', '')
            profile.campus = request.POST.get('campus', '')
            profile.admission_date = request.POST.get('admission_date') or None
        
        if request.FILES.get('profile_picture'):
            profile.profile_picture = request.FILES['profile_picture']
            
        profile.save()
        messages.success(request, "Your profile has been updated successfully.")
        return redirect('my_profile')

    return render(request, 'tenants/my_profile.html', {'profile': profile})

@login_required
def leadership_connect(request):
    """Module 7: Exclusive forum for School Leaders and Executive roles."""
    profile = get_object_or_404(Profile, user=request.user)
    if profile.role not in LEADERSHIP_ROLES:
        return render(request, 'tenants/access_denied.html', {
            'message': 'Leadership Connect is an exclusive forum for School Leaders.'
        }, status=403)

    threads = DiscussionThread.objects.all().select_related('created_by')
    if request.method == 'POST':
        title = request.POST.get('title')
        if title:
            DiscussionThread.objects.create(title=title, created_by=request.user)
            return redirect('leadership_connect')

    return render(request, 'tenants/leadership_connect.html', {'threads': threads})

@login_required
def thread_detail(request, pk):
    """View thread replies and post new ones."""
    profile = get_object_or_404(Profile, user=request.user)
    if profile.role not in LEADERSHIP_ROLES:
        return render(request, 'tenants/access_denied.html', status=403)

    thread = get_object_or_404(DiscussionThread, pk=pk)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content and not thread.is_locked:
            ThreadReply.objects.create(thread=thread, author=request.user, content=content)
            return redirect('thread_detail', pk=pk)
        
        takeaways = request.POST.get('key_takeaways')
        if takeaways and thread.created_by == request.user:
            thread.key_takeaways = takeaways
            thread.is_locked = True
            thread.save()
            return redirect('thread_detail', pk=pk)

    return render(request, 'tenants/thread_detail.html', {'thread': thread})

def home(request):
    if request.user.is_authenticated:
        return redirect('school_profile')
    return render(request, 'tenants/home.html')

def user_login(request):
    if request.user.is_authenticated:
        return redirect('school_profile')
    if request.method == 'POST':
        login_id = request.POST.get('username')
        password = request.POST.get('password')
        
        # Try authenticating with username
        user = authenticate(request, username=login_id, password=password)
        
        # If username fails, try authenticating with email
        if user is None:
            try:
                user_obj = User.objects.get(email=login_id)
                user = authenticate(request, username=user_obj.username, password=password)
            except (User.DoesNotExist, User.MultipleObjectsReturned):
                user = None
                
        if user is not None:
            login(request, user)
            return redirect('school_profile')
        else:
            return render(request, 'tenants/login.html', {'error': 'Invalid credentials'})
    return render(request, 'tenants/login.html')

def user_logout(request):
    logout(request)
    return redirect('home')

@user_passes_test(lambda u: u.is_superuser)
def master_dashboard(request):
    """Superuser dashboard to manage and view all schools."""
    schools = School.objects.annotate(
        user_count=Count('profiles', distinct=True),
        event_count=Count('events', distinct=True)
    ).order_by('name')
    
    # Add admin username to each school object for display
    for school in schools:
        admin_profile = Profile.objects.filter(school=school, role='school_leader').first()
        school.admin_username = admin_profile.user.username if admin_profile else "N/A"
    
    total_users = sum(s.user_count for s in schools)
    total_events = sum(s.event_count for s in schools)

    return render(request, 'tenants/master_dashboard.html', {
        'schools': schools,
        'total_users': total_users,
        'total_events': total_events,
        'all_schools': schools,  # for the school-selector dropdown to view an individual school's dashboard
    })

@login_required
def school_profile(request, pk=None):
    """Module 6: View and Edit School Profile."""
    if pk and request.user.is_superuser:
        school = get_object_or_404(School, pk=pk)
        can_edit = True # Superusers can edit anything
    else:
        try:
            profile = request.user.profile
            school = profile.school
            can_edit = profile.role in PROFILE_EDIT_ROLES
        except Profile.DoesNotExist:
            if request.user.is_superuser:
                messages.warning(request, "Superusers need a Profile to view their own school. Use the Master Dashboard to view other schools.")
                return redirect('master_dashboard')
            return render(request, 'tenants/access_denied.html', {'message': 'Your account is missing a profile.'})
    
    is_edit_mode = request.GET.get('edit') == '1'
    
    if request.method == 'POST' and can_edit:
        school.name = request.POST.get('name', school.name)
        school.address = request.POST.get('address', school.address)
        school.phone = request.POST.get('phone', school.phone)
        school.email = request.POST.get('email', school.email)
        school.location = request.POST.get('location', school.location)
        school.contact_person = request.POST.get('contact_person', school.contact_person)
        school.key_offerings = request.POST.get('key_offerings', school.key_offerings)
        if request.FILES.get('logo'):
            school.logo = request.FILES['logo']
        school.website = request.POST.get('website', school.website)
        school.linkedin_url = request.POST.get('linkedin_url', school.linkedin_url)
        school.facebook_url = request.POST.get('facebook_url', school.facebook_url)
        school.instagram_url = request.POST.get('instagram_url', school.instagram_url)
        school.save()
        log_activity(request.user, f"Updated school profile for {school.name}", school=school)
        messages.success(request, f"Profile for {school.name} updated successfully!")
        return redirect('school_profile')

    template = 'tenants/school_profile_edit.html' if (is_edit_mode and can_edit) else 'tenants/school_profile.html'
    return render(request, template, {'school': school, 'can_edit': can_edit})

@login_required
def notification_list(request):
    """M12: List all notifications for the current user."""
    notifications = request.user.notifications.all().order_by('-created_at')
    return render(request, 'tenants/notifications.html', {
        'notifications': notifications
    })

@login_required
def mark_notification_read(request, pk):
    """M12: Mark a specific notification as read."""
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.is_read = True
    notification.save()
    if notification.target_url:
        return redirect(notification.target_url)
    return redirect('notification_list')

@login_required
def school_network(request):
    """Module 6: Global Directory - view across all tenants."""
    schools = School.objects.all().order_by('name')
    return render(request, 'tenants/school_network.html', {'schools': schools})

@login_required
def review_dashboard(request):
    profile = get_object_or_404(Profile, user=request.user)
    if profile.role == 'student':
        return render(request, 'tenants/access_denied.html', {'message': 'Students do not have access to school review information.'})

    school = profile.school
    cycle_id = request.GET.get('cycle_id')
    review_cycles = ReviewCycle.objects.filter(school=school).order_by('-created_at')
    active_cycle = review_cycles.first()
    selected_cycle = get_object_or_404(review_cycles, pk=cycle_id) if cycle_id else active_cycle

    can_edit_review = profile.role in REVIEW_EDIT_ROLES
    can_create_cycle = profile.role in REVIEW_CYCLE_CREATE_ROLES
    is_archived_selection = selected_cycle is not None and active_cycle is not None and selected_cycle.pk != active_cycle.pk

    if request.method == 'POST' and selected_cycle and can_edit_review and not is_archived_selection:
        selected_cycle.self_study_status = request.POST.get('self_study_status')
        selected_cycle.self_study_start = request.POST.get('self_study_start') or None
        selected_cycle.self_study_end = request.POST.get('self_study_end') or None
        if request.FILES.get('self_study_document'):
            selected_cycle.self_study_document = request.FILES['self_study_document']
        selected_cycle.review_visit_status = request.POST.get('review_visit_status')
        selected_cycle.review_visit_start = request.POST.get('review_visit_start') or None
        selected_cycle.review_visit_end = request.POST.get('review_visit_end') or None
        if request.FILES.get('review_visit_document'):
            selected_cycle.review_visit_document = request.FILES['review_visit_document']
        selected_cycle.sip_status = request.POST.get('sip_status')
        selected_cycle.sip_start = request.POST.get('sip_start') or None
        selected_cycle.sip_end = request.POST.get('sip_end') or None
        if request.FILES.get('sip_document'):
            selected_cycle.sip_document = request.FILES['sip_document']
        selected_cycle.recommendations_status = request.POST.get('recommendations_status')
        selected_cycle.recommendations_start = request.POST.get('recommendations_start') or None
        selected_cycle.recommendations_end = request.POST.get('recommendations_end') or None
        if request.FILES.get('recommendations_document'):
            selected_cycle.recommendations_document = request.FILES['recommendations_document']
        selected_cycle.save()
        return redirect('review_dashboard')

    return render(request, 'tenants/review_dashboard.html', {
        'school': school,
        'review_cycle': selected_cycle,
        'active_cycle': active_cycle,
        'archived_cycles': review_cycles[1:] if active_cycle else [],
        'can_edit_review': can_edit_review,
        'can_create_cycle': can_create_cycle,
        'is_archived_selection': is_archived_selection,
        'selected_cycle_is_active': selected_cycle is not None and active_cycle is not None and selected_cycle.pk == active_cycle.pk,
        'review_status_choices': ReviewCycle._meta.get_field('self_study_status').choices,
    })

@login_required
def invite_user(request):
    """Module M1: School Admin invites teachers and students.
    Enforces max 2 admins and max 5 teachers per school."""
    profile = get_object_or_404(Profile, user=request.user)
    if profile.role not in ['admin', 'school_leader']:
        return render(request, 'tenants/access_denied.html', status=403)

    if request.method == 'POST':
        form = InvitationForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data['role']
            # Count existing members plus pending (unused) invitations, since a
            # Profile isn't created until the invitation is accepted.
            if role in PROFILE_EDIT_ROLES:
                current_admins = Profile.objects.filter(school=profile.school, role__in=PROFILE_EDIT_ROLES).count()
                pending_admins = Invitation.objects.filter(school=profile.school, role__in=PROFILE_EDIT_ROLES, is_used=False).count()
                if current_admins + pending_admins >= MAX_ADMINS_PER_SCHOOL:
                    messages.error(request, f"This school already has the maximum of {MAX_ADMINS_PER_SCHOOL} admins.")
                    return render(request, 'tenants/invite_user.html', {'form': form})
            elif role == 'teacher':
                current_teachers = Profile.objects.filter(school=profile.school, role='teacher').count()
                pending_teachers = Invitation.objects.filter(school=profile.school, role='teacher', is_used=False).count()
                if current_teachers + pending_teachers >= MAX_TEACHERS_PER_SCHOOL:
                    messages.error(request, f"This school already has the maximum of {MAX_TEACHERS_PER_SCHOOL} teachers. Remove one before adding another.")
                    return render(request, 'tenants/invite_user.html', {'form': form})

            invitation = form.save(commit=False)
            invitation.school = profile.school
            invitation.token = secrets.token_urlsafe(32)
            invitation.invited_by = request.user
            invitation.save()

            # In a real app, send email here
            invite_url = request.build_absolute_uri(
                reverse('accept_invitation', args=[invitation.token])
            )
            log_activity(request.user, f"Invited {invitation.email} as {invitation.get_role_display()}", school=profile.school)
            messages.success(request, f"Invitation created! Link: {invite_url}")
            return redirect('school_profile')
    else:
        form = InvitationForm()

    return render(request, 'tenants/invite_user.html', {'form': form})

def accept_invitation(request, token):
    """Module M1: Handle invitation link."""
    invitation = get_object_or_404(Invitation, token=token, is_used=False)
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            Profile.objects.create(
                user=user,
                school=invitation.school,
                role=invitation.role
            )
            
            invitation.is_used = True
            invitation.save()
            
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, "Welcome! Your account has been created.")
            return redirect('school_profile')
    else:
        form = UserRegistrationForm(initial={'email': invitation.email})
    
    return render(request, 'tenants/accept_invitation.html', {'form': form, 'invitation': invitation})

def school_registration(request):
    """Module M2: School Onboarding."""
    if request.method == 'POST':
        form = SchoolRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            school = form.save()
            
            # Create the Admin user for the school
            admin_email = form.cleaned_data['admin_email']
            admin_password = form.cleaned_data['admin_password']
            username = admin_email.split('@')[0]
            
            user = User.objects.create_user(
                username=username,
                email=admin_email,
                password=admin_password
            )
            
            Profile.objects.create(
                user=user,
                school=school,
                role='admin'
            )
            
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            log_activity(user, f"Registered school {school.name}", school=school)
            messages.success(request, f"Welcome! {school.name} has been registered.")
            return redirect('school_profile')
    else:
        form = SchoolRegistrationForm()

    return render(request, 'tenants/school_registration.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser)
def admin_create_school(request):
    """Super Admin creates the minimal school record (name, state/country, Yarra Coordinator),
    then invites the coordinator to complete the rest of the profile."""
    if request.method == 'POST':
        form = SchoolCreateForm(request.POST)
        if form.is_valid():
            school = form.save()

            invitation = Invitation.objects.create(
                school=school,
                email=school.yarra_coordinator_email,
                role='admin',
                token=secrets.token_urlsafe(32),
                invited_by=request.user,
            )
            invite_url = request.build_absolute_uri(
                reverse('accept_invitation', args=[invitation.token])
            )
            log_activity(request.user, f"Created school {school.name}", school=school)
            messages.success(request, f"{school.name} created. Invitation link for the Yarra Coordinator: {invite_url}")
            return redirect('master_dashboard')
    else:
        form = SchoolCreateForm()

    return render(request, 'tenants/admin_create_school.html', {'form': form})


@login_required
def complete_school_profile(request):
    """School Admin completes the extended profile (Google Form fields) after account creation."""
    profile = get_object_or_404(Profile, user=request.user)
    if profile.role not in PROFILE_EDIT_ROLES:
        return render(request, 'tenants/access_denied.html', status=403)

    school = profile.school
    extended, _ = SchoolProfileExtended.objects.get_or_create(school=school)

    if request.method == 'POST':
        form = SchoolProfileExtendedForm(request.POST, instance=extended)
        if form.is_valid():
            form.save()

            uploaded_files = request.FILES.getlist('documents')
            if len(uploaded_files) > 10:
                messages.error(request, "You can upload up to 10 files.")
                return render(request, 'tenants/complete_school_profile.html', {'form': form, 'school': school})
            for f in uploaded_files:
                SchoolDocument.objects.create(school=school, file=f, uploaded_by=request.user)

            school.profile_completed = True
            school.save(update_fields=['profile_completed'])
            log_activity(request.user, f"Completed school profile for {school.name}", school=school)
            messages.success(request, "School profile completed. Thank you!")
            return redirect('school_profile')
    else:
        form = SchoolProfileExtendedForm(instance=extended)

    return render(request, 'tenants/complete_school_profile.html', {'form': form, 'school': school})


@login_required
def user_management(request):
    """Super Admin: view users across all schools. School Admin: view own school's users only."""
    if request.user.is_superuser:
        profiles = Profile.objects.select_related('user', 'school').order_by('school__name', 'role')
        recent_activity = ActivityLog.objects.select_related('user', 'school')[:50]
        return render(request, 'tenants/user_management.html', {
            'profiles': profiles,
            'recent_activity': recent_activity,
            'max_admins': MAX_ADMINS_PER_SCHOOL,
            'max_teachers': MAX_TEACHERS_PER_SCHOOL,
        })

    profile = get_object_or_404(Profile, user=request.user)
    if profile.role not in PROFILE_EDIT_ROLES:
        return render(request, 'tenants/access_denied.html', status=403)

    profiles = Profile.objects.filter(school=profile.school).select_related('user').order_by('role')
    recent_activity = ActivityLog.objects.filter(school=profile.school).select_related('user', 'school')[:50]

    return render(request, 'tenants/user_management.html', {
        'profiles': profiles,
        'recent_activity': recent_activity,
        'max_admins': MAX_ADMINS_PER_SCHOOL,
        'max_teachers': MAX_TEACHERS_PER_SCHOOL,
    })


@login_required
def record_payment(request):
    """School Admin and Super Admin can record a manual payment (including cheque)."""
    profile = None
    if not request.user.is_superuser:
        profile = get_object_or_404(Profile, user=request.user)
        if profile.role not in PROFILE_EDIT_ROLES:
            return render(request, 'tenants/access_denied.html', status=403)

    if request.method == 'POST':
        form = PaymentForm(request.POST, request.FILES)
        if not request.user.is_superuser:
            form.data = form.data.copy()
            form.data['school'] = profile.school_id
        if form.is_valid():
            payment = form.save(commit=False)
            if not request.user.is_superuser:
                payment.school = profile.school
            payment.recorded_by = request.user
            payment.save()
            log_activity(request.user, f"Recorded a {payment.get_method_display()} payment of {payment.amount} for {payment.school.name}", school=payment.school)
            messages.success(request, "Payment recorded.")
            return redirect('user_management')
    else:
        form = PaymentForm()
        if not request.user.is_superuser:
            del form.fields['school']

    return render(request, 'tenants/record_payment.html', {'form': form})

@login_required
def create_review_cycle(request):
    profile = get_object_or_404(Profile, user=request.user)
    if profile.role not in REVIEW_CYCLE_CREATE_ROLES:
        return render(request, 'tenants/access_denied.html', {'message': 'Only School Leaders and Admins can create new review cycles.'})
    if request.method == 'POST':
        review_cycle = ReviewCycle.objects.create(
            school=profile.school,
            title=request.POST.get('title', 'Review Cycle'),
            start_date=request.POST.get('start_date') or None,
            end_date=request.POST.get('end_date') or None,
        )
        return redirect(f"{reverse('review_dashboard')}?cycle_id={review_cycle.pk}")
    return render(request, 'tenants/review_cycle_form.html', {'school': profile.school})

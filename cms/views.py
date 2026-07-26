from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import ContentItem, Category, Comment
from .forms import ContentSubmitForm
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.shortcuts import redirect
from tenants.notifications import create_notification, log_activity, notify_superadmins

@login_required
def content_library(request):
    """M8: Searchable, filterable repository of all content."""
    query = request.GET.get('q')
    content_type = request.GET.get('type')
    category_slug = request.GET.get('category')
    
    items = ContentItem.objects.filter(status='published')
    
    # Access Control: Early Years check
    profile = request.user.profile
    if not profile.school.signed_up_for_early_years:
        items = items.exclude(is_early_years_only=True)
        
    # Access Control: Targeted schools check
    items = items.filter(Q(target_schools=profile.school) | Q(target_schools__isnull=True))
    
    if query:
        items = items.filter(
            Q(title__icontains=query) | 
            Q(body__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()
        
    if content_type:
        items = items.filter(content_type=content_type)
        
    if category_slug:
        items = items.filter(category__slug=category_slug)
        
    categories = Category.objects.all()
    
    return render(request, 'cms/content_library.html', {
        'items': items,
        'categories': categories,
        'selected_type': content_type,
        'selected_category': category_slug,
        'query': query
    })

@login_required
def content_submit(request):
    """School staff submit content for the library; it goes to Pending Yarra Verification
    until a Super Admin approves it, per Chelli's requirement."""
    if request.method == 'POST':
        form = ContentSubmitForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.author = request.user
            item.status = 'pending_verification'
            item.save()
            form.save_m2m()
            notify_superadmins(
                title='Content pending verification',
                message=f"{request.user.username} submitted '{item.title}' for verification.",
                target_url=f"/cms/review/",
            )
            log_activity(request.user, f"Submitted content '{item.title}' for Yarra verification", school=request.user.profile.school)
            messages.success(request, "Your content has been submitted and is pending Yarra verification.")
            return redirect('content_library')
    else:
        form = ContentSubmitForm()

    return render(request, 'cms/content_submit.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser)
def content_review_queue(request):
    """Super Admin approves or rejects content pending Yarra verification."""
    pending_items = ContentItem.objects.filter(status='pending_verification').select_related('author').order_by('-created_at')
    return render(request, 'cms/content_review_queue.html', {'pending_items': pending_items})


@user_passes_test(lambda u: u.is_superuser)
def content_review_decide(request, slug):
    item = get_object_or_404(ContentItem, slug=slug, status='pending_verification')
    if request.method == 'POST':
        decision = request.POST.get('decision')
        if decision == 'approve':
            item.status = 'published'
            item.save(update_fields=['status'])
            if item.author:
                create_notification(
                    recipient=item.author,
                    title='Content approved',
                    message=f"Your content '{item.title}' has been verified and published.",
                    level='success',
                    target_url=f"/cms/content/{item.slug}/",
                )
            messages.success(request, f"'{item.title}' approved and published.")
        elif decision == 'reject':
            item.status = 'draft'
            item.save(update_fields=['status'])
            if item.author:
                create_notification(
                    recipient=item.author,
                    title='Content rejected',
                    message=f"Your content '{item.title}' was not approved and has been returned to draft.",
                    level='warning',
                    target_url=f"/cms/content/{item.slug}/",
                )
            messages.success(request, f"'{item.title}' rejected.")
    return redirect('content_review_queue')


@login_required
def content_detail(request, slug):
    """Display a single content item with comments."""
    item = get_object_or_404(ContentItem, slug=slug, status='published')
    
    # Access Control check
    profile = request.user.profile
    if item.is_early_years_only and not profile.school.signed_up_for_early_years:
        messages.error(request, "This content is reserved for Early Years members.")
        return redirect('content_library')
        
    if item.target_schools.exists() and profile.school not in item.target_schools.all():
        messages.error(request, "You do not have access to this content.")
        return redirect('content_library')
        
    content_type = ContentType.objects.get_for_model(item)
    comments = Comment.objects.filter(content_type=content_type, object_id=item.id, parent__isnull=True)
    
    if request.method == 'POST':
        body = request.POST.get('body')
        if body:
            Comment.objects.create(
                content_type=content_type,
                object_id=item.id,
                user=request.user,
                body=body
            )
            messages.success(request, "Comment added.")
            return redirect('content_detail', slug=slug)
            
    return render(request, 'cms/content_detail.html', {
        'item': item,
        'comments': comments
    })

from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import ContentItem, Category, Comment
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect

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

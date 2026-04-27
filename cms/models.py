from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from tenants.models import School
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class ContentItem(models.Model):
    CONTENT_TYPES = [
        ('article', 'Article'),
        ('announcement', 'Announcement'),
        ('podcast', 'Podcast Episode'),
        ('video', 'Video'),
        ('page', 'Static Page'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    body = models.TextField(help_text="Rich text content")
    featured_image = models.ImageField(upload_to='cms/featured/', blank=True, null=True)
    
    # Media specific
    video_url = models.URLField(blank=True, null=True, help_text="YouTube/Vimeo link")
    audio_file = models.FileField(upload_to='cms/audio/', blank=True, null=True)
    
    # Metadata
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='items')
    tags = models.ManyToManyField(Tag, blank=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    # SEO
    seo_title = models.CharField(max_length=70, blank=True)
    seo_description = models.CharField(max_length=160, blank=True)
    
    # Access Control
    is_early_years_only = models.BooleanField(default=False)
    target_schools = models.ManyToManyField(School, blank=True, help_text="Leave empty for all schools")
    
    # Scheduling
    publish_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-publish_at']

    def __str__(self):
        return self.title

    @property
    def is_published(self):
        return self.status == 'published' and self.publish_at <= timezone.now()

class Comment(models.Model):
    # Link to ContentItem or Event using GenericForeignKey
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cms_comments')
    body = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    likes = models.ManyToManyField(User, blank=True, related_name='liked_comments')
    is_flagged = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.user.username} on {self.content_object}"

    @property
    def school_name(self):
        try:
            return self.user.profile.school.name
        except:
            return "Unknown School"

from django import forms
from .models import ContentItem

class ContentSubmitForm(forms.ModelForm):
    class Meta:
        model = ContentItem
        fields = ['title', 'slug', 'content_type', 'body', 'featured_image', 'video_url', 'audio_file', 'category', 'tags']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 8}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].required = False

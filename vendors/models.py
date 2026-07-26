from django.db import models

class VendorCategory(models.TextChoices):
    UNIFORMS = 'uniforms', 'Uniforms'
    BOOKS_STATIONERY = 'books_stationery', 'Books & Stationery'
    EDTECH = 'edtech', 'EdTech'
    FURNITURE = 'furniture', 'Furniture & Fixtures'
    TRANSPORT = 'transport', 'Transport'
    CANTEEN = 'canteen', 'Canteen Supplies'
    SPORTS = 'sports', 'Sports Equipment'
    LAB_SUPPLIES = 'lab', 'Lab Supplies'
    INFRASTRUCTURE = 'infrastructure', 'Digital Infrastructure'
    OTHER = 'other', 'Other'

class Vendor(models.Model):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=VendorCategory.choices)
    description = models.TextField()
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to='vendor_logos/', blank=True, null=True)
    consortium_offer = models.TextField(help_text="Special deal/discount for consortium members")
    is_vetted = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class VendorPromotion(models.Model):
    PLACEMENT_CHOICES = [
        ('homepage', 'Homepage Banner'),
        ('directory', 'Category Page Banner'),
        ('sidebar', 'Sidebar Spotlight'),
    ]

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='promotions')
    title = models.CharField(max_length=200)
    banner_image = models.ImageField(upload_to='vendor_promotions/')
    offer_text = models.TextField()
    cta_link = models.URLField()
    placement = models.CharField(max_length=20, choices=PLACEMENT_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.vendor.name} - {self.title}"

class VendorEnquiry(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('responded', 'Responded'),
    ]

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='enquiries')
    school = models.ForeignKey('tenants.School', on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Enquiry for {self.vendor.name} from {self.school.name}"


class EventInterest(models.Model):
    """A vendor marking interest in participating in an upcoming Yarra event."""
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='event_interests')
    event = models.ForeignKey('competitions.Event', on_delete=models.CASCADE, related_name='vendor_interests')
    submitted_by = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    message = models.TextField(blank=True, help_text="Why the vendor wants to be involved")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.vendor.name} interested in {self.event.title}"

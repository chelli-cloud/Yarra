from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('tenants', '0004_notification'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('category', models.CharField(choices=[('action', 'Yarra Action'), ('spotlight', 'Yarra Spotlight'), ('active', 'Yarra Active')], max_length=20)),
                ('registration_link', models.URLField(help_text='Google Form URL for registration')),
                ('brochure', models.FileField(blank=True, null=True, upload_to='competitions/brochures/')),
                ('payment_qr', models.FileField(blank=True, help_text='UPI QR code for payment', null=True, upload_to='competitions/payment_qr/')),
                ('razorpay_payment_link', models.URLField(blank=True, help_text='Razorpay payment page URL (optional)')),
                ('winners', models.TextField(blank=True, help_text='Finalist/winner details')),
                ('winning_resources', models.FileField(blank=True, help_text='Photos, PDFs of winning entries', null=True, upload_to='competitions/winners/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=models.deletion.SET_NULL, related_name='created_events', to=settings.AUTH_USER_MODEL)),
                ('school', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='events', to='tenants.school')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='CompetitionResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_name', models.CharField(max_length=100)),
                ('prize', models.CharField(help_text='e.g., 1st Place, 2nd Place, Runner-up', max_length=50)),
                ('announced_at', models.DateTimeField(auto_now_add=True)),
                ('event', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='results', to='competitions.event')),
                ('school', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='competition_results', to='tenants.school')),
            ],
            options={
                'ordering': ['-announced_at'],
            },
        ),
        migrations.CreateModel(
            name='StudentRegistration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('razorpay_payment_id', models.CharField(blank=True, max_length=50)),
                ('razorpay_signature', models.CharField(blank=True, max_length=200)),
                ('razorpay_order_id', models.CharField(blank=True, max_length=50)),
                ('payment_status', models.CharField(choices=[('pending', 'Pending'), ('verified', 'Verified'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('payment_screenshot', models.FileField(blank=True, null=True, upload_to='competitions/payment_screenshots/')),
                ('registered_at', models.DateTimeField(auto_now_add=True)),
                ('event', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='registrations', to='competitions.event')),
                ('student', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='event_registrations', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-registered_at'],
                'unique_together': {('event', 'student')},
            },
        ),
        migrations.AddIndex(
            model_name='event',
            index=models.Index(fields=['category', 'is_active'], name='competition_categor_ef7628_idx'),
        ),
        migrations.AddIndex(
            model_name='event',
            index=models.Index(fields=['school', 'is_active'], name='competition_school__16ac24_idx'),
        ),
        migrations.AddIndex(
            model_name='competitionresult',
            index=models.Index(fields=['school', '-announced_at'], name='competition_school__6cb929_idx'),
        ),
        migrations.AddIndex(
            model_name='competitionresult',
            index=models.Index(fields=['event', 'school'], name='competition_event_i_57a516_idx'),
        ),
        migrations.AddIndex(
            model_name='studentregistration',
            index=models.Index(fields=['event', 'payment_status'], name='competition_event_i_7b8a97_idx'),
        ),
        migrations.AddIndex(
            model_name='studentregistration',
            index=models.Index(fields=['student', 'payment_status'], name='competition_student_9d613f_idx'),
        ),
    ]

import json
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from competitions.models import CompetitionResult, Event, PaymentStatus, StudentRegistration
from tenants.models import Notification, Profile, School


class CompetitionModuleTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(
            name='Central High School',
            address='123 Main Street',
            phone='555-0101',
            email='info@example.com',
        )
        self.other_school = School.objects.create(
            name='Riverside Academy',
            address='456 River Road',
            phone='555-0202',
            email='riverside@example.com',
        )

        self.teacher = User.objects.create_user(username='teacher', password='test@1234')
        Profile.objects.create(user=self.teacher, school=self.school, role='teacher')

        self.school_leader = User.objects.create_user(username='leader', password='test@1234')
        Profile.objects.create(user=self.school_leader, school=self.school, role='school_leader')

        self.student = User.objects.create_user(username='student', password='test@1234')
        Profile.objects.create(user=self.student, school=self.school, role='student')

        self.other_student = User.objects.create_user(username='otherstudent', password='test@1234')
        Profile.objects.create(user=self.other_student, school=self.other_school, role='student')

        self.superuser = User.objects.create_superuser(username='superadmin', email='super@example.com', password='test@1234')

        self.event = Event.objects.create(
            school=self.school,
            created_by=self.teacher,
            title='Debate Championship',
            description='Inter-school debate event',
            category='spotlight',
            registration_link='https://forms.example.com/debate',
            is_active=True,
        )

    def test_superuser_can_create_event(self):
        self.client.login(username='superadmin', password='test@1234')
        response = self.client.post(reverse('event_create'), {
            'title': 'Science Fair',
            'description': 'Students present projects',
            'category': 'active',
            'registration_link': 'https://forms.example.com/science',
            'razorpay_payment_link': '',
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Event.objects.filter(title='Science Fair').exists())

    def test_teacher_cannot_create_event(self):
        # Events are Yarra-wide now; only Super Admin creates them.
        self.client.login(username='teacher', password='test@1234')
        response = self.client.post(reverse('event_create'), {
            'title': 'Blocked Event',
            'description': 'Should not be created',
            'category': 'active',
            'registration_link': 'https://forms.example.com/blocked',
            'razorpay_payment_link': '',
        })

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Event.objects.filter(title='Blocked Event').exists())

    def test_student_cannot_create_event(self):
        self.client.login(username='student', password='test@1234')
        response = self.client.get(reverse('event_create'))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Event.objects.filter(title='Blocked Event').exists())

    def test_student_can_register_for_event(self):
        self.client.login(username='student', password='test@1234')
        response = self.client.post(reverse('register_for_event', args=[self.event.pk]), {})

        self.assertEqual(response.status_code, 302)
        registration = StudentRegistration.objects.get(event=self.event, student=self.student)
        self.assertEqual(registration.payment_status, PaymentStatus.PENDING)

    def test_other_school_student_can_register(self):
        # Events are Yarra-wide now; any school's students can register for any active event.
        self.client.login(username='otherstudent', password='test@1234')
        response = self.client.post(reverse('register_for_event', args=[self.event.pk]), {})

        self.assertEqual(response.status_code, 302)
        self.assertTrue(StudentRegistration.objects.filter(event=self.event, student=self.other_student).exists())

    def test_superuser_can_delete_event_and_cascades_registrations(self):
        StudentRegistration.objects.create(event=self.event, student=self.student)
        self.client.login(username='superadmin', password='test@1234')
        response = self.client.post(reverse('event_delete', args=[self.event.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Event.objects.filter(pk=self.event.pk).exists())
        self.assertFalse(StudentRegistration.objects.filter(student=self.student).exists())

    def test_teacher_cannot_delete_event(self):
        self.client.login(username='teacher', password='test@1234')
        response = self.client.post(reverse('event_delete', args=[self.event.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Event.objects.filter(pk=self.event.pk).exists())

    def test_result_creation_notifies_school_leader(self):
        CompetitionResult.objects.create(
            event=self.event,
            school=self.school,
            student_name='Asha',
            prize='1st Place',
        )

        self.assertTrue(Notification.objects.filter(recipient=self.school_leader, title='Competition result announced').exists())

    @patch('competitions.webhooks.razorpay.Client')
    def test_razorpay_webhook_verifies_payment(self, client_cls):
        registration = StudentRegistration.objects.create(
            event=self.event,
            student=self.student,
            razorpay_order_id='order_123',
        )

        client = client_cls.return_value
        client.utility.verify_webhook_signature.return_value = None

        payload = {
            'payload': {
                'payment': {
                    'entity': {
                        'id': 'pay_123',
                        'order_id': 'order_123',
                        'status': 'captured',
                    }
                }
            }
        }

        response = self.client.post(
            reverse('razorpay_webhook'),
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_X_RAZORPAY_SIGNATURE='valid',
        )

        self.assertEqual(response.status_code, 200)
        registration.refresh_from_db()
        self.assertEqual(registration.payment_status, PaymentStatus.VERIFIED)

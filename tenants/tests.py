from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Profile, ReviewCycle, School, SelfEvaluationResponse


class ReviewDashboardTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(
            name='Central High School',
            address='123 Main Street',
            phone='555-0101',
            email='info@example.com',
        )

        self.leader = User.objects.create_user(username='leader', password='test@1234')
        Profile.objects.create(user=self.leader, school=self.school, role='school_leader')

        self.teacher = User.objects.create_user(username='teacher', password='test@1234')
        Profile.objects.create(user=self.teacher, school=self.school, role='teacher')

    def test_teacher_blocked_from_review_dashboard(self):
        self.client.login(username='teacher', password='test@1234')
        response = self.client.get(reverse('review_dashboard'))

        self.assertEqual(response.status_code, 403)

    def test_leader_visiting_review_dashboard_auto_creates_cycle(self):
        self.client.login(username='leader', password='test@1234')
        response = self.client.get(reverse('review_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(ReviewCycle.objects.filter(school=self.school).exists())
        self.assertContains(response, 'Part A')
        self.assertContains(response, 'Part D')

    def test_teacher_blocked_from_self_evaluation_form(self):
        self.client.login(username='teacher', password='test@1234')
        response = self.client.get(reverse('self_evaluation_form'), {'part': 'A'})

        self.assertEqual(response.status_code, 403)

    def test_self_evaluation_form_requires_valid_part(self):
        self.client.login(username='leader', password='test@1234')
        response = self.client.get(reverse('self_evaluation_form'))

        self.assertEqual(response.status_code, 302)

    def test_self_evaluation_saves_only_submitted_part_and_preserves_others(self):
        self.client.login(username='leader', password='test@1234')

        self.client.post(reverse('self_evaluation_form'), {'part': 'A', 'A-1.1': 'Central High School'})
        self.client.post(reverse('self_evaluation_form'), {'part': 'D', 'D-1': 'Improve attendance.'})

        cycle = ReviewCycle.objects.get(school=self.school)
        response = SelfEvaluationResponse.objects.get(review_cycle=cycle)

        self.assertEqual(response.data.get('A-1.1'), 'Central High School')
        self.assertEqual(response.data.get('D-1'), 'Improve attendance.')

    def test_review_dashboard_shows_progress_after_partial_save(self):
        self.client.login(username='leader', password='test@1234')
        self.client.post(reverse('self_evaluation_form'), {'part': 'A', 'A-1.1': 'Central High School'})

        response = self.client.get(reverse('review_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'In Progress')

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Profile, ReviewCycle, School


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

        self.archived_cycle = ReviewCycle.objects.create(
            school=self.school,
            title='2025 Review Cycle',
            self_study_status='completed',
        )
        self.active_cycle = ReviewCycle.objects.create(
            school=self.school,
            title='2026 Review Cycle',
            self_study_status='in_progress',
        )

    def test_dashboard_does_not_autocreate_cycle_for_empty_school(self):
        empty_school = School.objects.create(
            name='New School',
            address='456 New Road',
            phone='555-0202',
            email='new@example.com',
        )
        user = User.objects.create_user(username='admin', password='test@1234')
        Profile.objects.create(user=user, school=empty_school, role='admin')

        self.client.login(username='admin', password='test@1234')
        response = self.client.get(reverse('review_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No review cycle exists yet for this school.')
        self.assertEqual(ReviewCycle.objects.filter(school=empty_school).count(), 0)

    def test_create_review_cycle_route_available_to_school_leader(self):
        self.client.login(username='leader', password='test@1234')
        response = self.client.post(reverse('create_review_cycle'), {
            'title': '2027 Review Cycle',
            'start_date': '2027-01-01',
            'end_date': '2027-12-31',
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(ReviewCycle.objects.filter(school=self.school, title='2027 Review Cycle').exists())

    def test_archive_list_shows_past_cycles(self):
        self.client.login(username='leader', password='test@1234')
        response = self.client.get(reverse('review_dashboard'), {'cycle_id': self.active_cycle.pk})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Past Review Archive')
        self.assertContains(response, self.archived_cycle.title)

    def test_archived_cycle_is_read_only_even_for_leader(self):
        self.client.login(username='leader', password='test@1234')
        response = self.client.post(f"{reverse('review_dashboard')}?cycle_id={self.archived_cycle.pk}", {
            'self_study_status': 'not_started',
            'review_visit_status': self.archived_cycle.review_visit_status,
            'review_visit_start': '',
            'review_visit_end': '',
            'sip_status': self.archived_cycle.sip_status,
            'sip_start': '',
            'sip_end': '',
            'recommendations_status': self.archived_cycle.recommendations_status,
            'recommendations_start': '',
            'recommendations_end': '',
        })

        self.assertEqual(response.status_code, 200)
        self.archived_cycle.refresh_from_db()
        self.assertEqual(self.archived_cycle.self_study_status, 'completed')

    def test_teacher_has_view_only_access_to_review_cycle(self):
        self.client.login(username='teacher', password='test@1234')
        response = self.client.post(reverse('review_dashboard'), {
            'self_study_status': 'completed',
        })

        self.assertEqual(response.status_code, 200)
        self.active_cycle.refresh_from_db()
        self.assertEqual(self.active_cycle.self_study_status, 'in_progress')

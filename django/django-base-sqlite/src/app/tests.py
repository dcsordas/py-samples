from django.test import TestCase
from django.urls import reverse


class IndexViewTest(TestCase):
    def test_ok(self):
        response = self.client.get(reverse('app:index'))
        self.assertContains(response, "It's alive")
        self.assertTrue(response.context['status_report'])

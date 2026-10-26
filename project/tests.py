from django.test import TestCase
from django.urls import reverse

from .models import SavedPrediction, Team


class SmokeTests(TestCase):
    fixtures = ["ucl_data"]

    def test_public_pages_render(self):
        team = Team.objects.first()
        urls = [
            reverse("project:home"),
            reverse("project:team_list"),
            reverse("project:team_detail", args=[team.pk]),
            reverse("project:player_list"),
            reverse("project:match_list"),
            reverse("project:match_detail", args=[1]),
            reverse("project:predictor"),
            reverse("project:signup"),
            reverse("login"),
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_saved_predictions_requires_login(self):
        response = self.client.get(reverse("project:saved_predictions"))
        self.assertEqual(response.status_code, 302)

    def test_signup_predict_save_delete(self):
        response = self.client.post(reverse("project:signup"), {
            "username": "testfan",
            "password1": "pitch-lime-2026!",
            "password2": "pitch-lime-2026!",
        })
        self.assertRedirects(response, reverse("project:home"))

        real, city = Team.objects.get(name="Real Madrid"), Team.objects.get(name="Manchester City")
        response = self.client.post(reverse("project:predictor"), {"team_a": real.pk, "team_b": city.pk})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "model confidence")
        self.assertEqual(SavedPrediction.objects.count(), 1)

        self.assertContains(self.client.get(reverse("project:saved_predictions")), "Real Madrid")

        prediction = SavedPrediction.objects.get()
        self.client.post(reverse("project:delete_prediction", args=[prediction.pk]))
        self.assertEqual(SavedPrediction.objects.count(), 0)

    def test_same_team_is_rejected(self):
        team = Team.objects.first()
        response = self.client.post(reverse("project:predictor"), {"team_a": team.pk, "team_b": team.pk})
        self.assertContains(response, "Teams must be different")

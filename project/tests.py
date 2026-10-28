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


class RankingTests(TestCase):
    def setUp(self):
        self.team = Team.objects.create(name="Test FC", country="X", league="Y")

    def player(self, name, goals, assists, matches):
        from .models import PlayerRanking
        return PlayerRanking.objects.create(
            player_name=name, team=self.team, season="2025-26",
            goals=goals, assists=assists, matches_played=matches,
        )

    def ranking(self):
        from .rankings import ranked_players
        return [(p.player_name, p.rank) for p in ranked_players()]

    def test_orders_by_contributions_per_match(self):
        self.player("Low", 2, 0, 10)     # 0.20
        self.player("High", 9, 3, 10)    # 1.20
        self.player("Mid", 5, 0, 10)     # 0.50
        self.assertEqual(self.ranking(), [("High", 1), ("Mid", 2), ("Low", 3)])

    def test_tie_breakers_and_shared_ranks(self):
        self.player("More goals", 7, 2, 10)    # 0.90, 9 G+A, 7 goals
        self.player("Fewer goals", 6, 3, 10)   # 0.90, 9 G+A, 6 goals
        self.player("Exact tie A", 5, 0, 10)
        self.player("Exact tie B", 5, 0, 10)
        self.assertEqual(self.ranking(), [
            ("More goals", 1), ("Fewer goals", 2), ("Exact tie A", 3), ("Exact tie B", 3),
        ])

    def test_too_few_appearances_do_not_qualify(self):
        self.player("Regular", 6, 0, 12)       # most matches = 12, so 4 needed
        self.player("Cameo", 2, 0, 1)          # 2.00 per match but only 1 app
        self.assertEqual(self.ranking(), [("Regular", 1)])

    def test_only_latest_season_is_ranked(self):
        from .models import PlayerRanking
        PlayerRanking.objects.create(player_name="Old", team=self.team, season="2024-25",
                                     goals=20, assists=0, matches_played=10)
        self.player("Current", 3, 0, 10)
        self.assertEqual(self.ranking(), [("Current", 1)])


class SeasonSwitchTests(TestCase):
    fixtures = ["ucl_data"]

    def test_current_season_is_default_and_past_season_selectable(self):
        from .rankings import available_seasons
        seasons = available_seasons()
        self.assertGreaterEqual(len(seasons), 2)
        self.assertEqual(seasons, sorted(seasons, reverse=True))

        default = self.client.get(reverse("project:player_list"))
        self.assertEqual(default.context["season"], seasons[0])
        self.assertTrue(default.context["is_current"])

        past = self.client.get(reverse("project:player_list"), {"season": seasons[1]})
        self.assertEqual(past.context["season"], seasons[1])
        self.assertFalse(past.context["is_current"])
        self.assertTrue(all(p.season == seasons[1] for p in past.context["players"]))

    def test_unknown_season_falls_back_to_current(self):
        response = self.client.get(reverse("project:player_list"), {"season": "1999-00"})
        self.assertEqual(response.context["season"], response.context["seasons"][0])

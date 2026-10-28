"""Player ranking logic.

Ranks are never stored. They are computed from each player's raw stats
every time a ranking is requested, so the order always follows the data.

Rule
----
- Pool: players from one season (the most recent on record by default).
- Score: goal contributions per match = (goals + assists) / matches played.
  (football-data.org doesn't provide minutes played, so a true per-90 rate
  isn't available.)
- Qualifying: a player must have played at least MIN_SHARE_OF_MATCHES of the
  most matches anyone in the pool played, so one goal in one appearance
  can't top the table.
- Order: score, then total goal contributions, then goals, then fewer
  matches (same output in fewer games ranks higher), then name.
- Ties on score, contributions and goals share a rank (1, 2, 2, 4).
"""

from math import ceil

from django.db.models import F, FloatField, Max, Window
from django.db.models.functions import Cast, Rank

from .models import PlayerRanking

MIN_SHARE_OF_MATCHES = 1 / 3


def available_seasons():
    """Seasons that have player stats, newest first, e.g. ['2026-27', '2025-26']."""
    return list(
        PlayerRanking.objects.exclude(season="")
        .order_by("-season")
        .values_list("season", flat=True)
        .distinct()
    )


def current_season():
    """The most recent season that has player stats."""
    seasons = available_seasons()
    return seasons[0] if seasons else None


def min_matches_for(players):
    most = players.aggregate(most=Max("matches_played"))["most"] or 0
    return max(1, ceil(most * MIN_SHARE_OF_MATCHES))


def ranked_players(season=None):
    """Qualifying players for a season, best first, each annotated with
    `rank`, `contributions` and `per_match`."""
    season = season or current_season()
    pool = PlayerRanking.objects.filter(season=season).select_related("team")
    qualified = pool.filter(matches_played__gte=min_matches_for(pool))

    contributions = F("goals") + F("assists")
    per_match = Cast(contributions, FloatField()) / Cast(F("matches_played"), FloatField())
    order = [F("per_match").desc(), F("contributions").desc(), F("goals").desc()]

    return (
        qualified.annotate(contributions=contributions, per_match=per_match)
        .annotate(rank=Window(expression=Rank(), order_by=order))
        .order_by(*order, "matches_played", "player_name")
    )

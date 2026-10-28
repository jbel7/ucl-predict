"""Pull Champions League player stats from football-data.org.

Usage:
    python manage.py sync_players              # current season
    python manage.py sync_players --season 2025  # the 2025-26 season

Needs FOOTBALL_DATA_API_KEY. Stores raw stats only (goals, assists,
matches played); rankings are computed from them in project.rankings.
Only players from clubs already in the database are kept.
"""

import time
import unicodedata

import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from project.models import PlayerRanking, Team

API = "https://api.football-data.org/v4"

# Our club names where they differ from football-data.org's.
TEAM_ALIASES = {
    "bayern munich": "fc bayern munchen",
    "inter milan": "fc internazionale milano",
    "psg": "paris saint-germain fc",
}

# football-data.org position/section names -> PlayerRanking.position
POSITIONS = {
    "goalkeeper": "GK",
    "defence": "DEF", "defender": "DEF", "back": "DEF",
    "midfield": "MID", "midfielder": "MID",
    "offence": "FWD", "forward": "FWD", "winger": "FWD", "striker": "FWD",
}


def normalize(name):
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return " ".join(ascii_name.lower().replace(".", "").split())


def map_position(raw):
    raw = (raw or "").lower()
    for key, code in POSITIONS.items():
        if key in raw:
            return code
    return ""


class Command(BaseCommand):
    help = "Fetch Champions League scorers from football-data.org and store their stats"

    def add_arguments(self, parser):
        parser.add_argument("--season", type=int, help="Start year of the season, e.g. 2025 for 2025-26")
        parser.add_argument("--limit", type=int, default=100, help="How many top scorers to request")

    def handle(self, *args, season=None, limit=100, **options):
        key = settings.FOOTBALL_DATA_API_KEY
        if not key:
            raise CommandError("Set FOOTBALL_DATA_API_KEY to sync player stats.")
        self.session = requests.Session()
        self.session.headers["X-Auth-Token"] = key

        params = {"limit": limit}
        if season:
            params["season"] = season
        data = self.get("/competitions/CL/scorers", params)

        start, end = data["season"]["startDate"][:4], data["season"]["endDate"][2:4]
        season_label = f"{start}-{end}"
        teams = self.team_lookup()

        kept, skipped = [], 0
        for entry in data.get("scorers", []):
            team = self.match_team(entry["team"], teams)
            if team is None:
                skipped += 1
                continue
            kept.append((entry, team))

        with transaction.atomic():
            seen, changed = [], 0
            for entry, team in kept:
                person = entry["player"]
                stats = {
                    "player_name": person["name"],
                    "team": team,
                    "goals": entry.get("goals") or 0,
                    "assists": entry.get("assists") or 0,
                    "penalties": entry.get("penalties") or 0,
                    "matches_played": entry.get("playedMatches") or 0,
                }
                player, created = PlayerRanking.objects.get_or_create(
                    api_id=person["id"], season=season_label, defaults=stats,
                )
                # Only write when something changed, so updated_at (and the
                # fixture the daily sync commits) stays put on quiet days.
                if created:
                    changed += 1
                elif any(getattr(player, k) != v for k, v in stats.items()):
                    for k, v in stats.items():
                        setattr(player, k, v)
                    player.save()
                    changed += 1
                seen.append(player.pk)
            # Players who dropped out of this season's list, plus any
            # hand-entered rows with no season, no longer belong in the table.
            stale = PlayerRanking.objects.filter(season__in=[season_label, ""]).exclude(pk__in=seen)
            removed = stale.count()
            stale.delete()

        self.fill_positions(PlayerRanking.objects.filter(pk__in=seen, position=""))

        self.stdout.write(self.style.SUCCESS(
            f"{season_label}: {len(seen)} players from our clubs, {changed} new or updated "
            f"({skipped} from other clubs skipped, {removed} stale rows removed)."
        ))

    # --- helpers -----------------------------------------------------------

    def get(self, path, params=None):
        response = self.session.get(f"{API}{path}", params=params, timeout=20)
        if response.status_code == 429:
            wait = int(response.headers.get("X-RequestCounter-Reset", 60))
            self.stdout.write(f"Rate limited, waiting {wait}s...")
            time.sleep(wait + 1)
            return self.get(path, params)
        if not response.ok:
            message = response.json().get("message", response.text) if response.content else response.reason
            raise CommandError(f"football-data.org returned {response.status_code}: {message}")
        if response.headers.get("X-Requests-Available-Minute") == "0":
            time.sleep(int(response.headers.get("X-RequestCounter-Reset", 60)) + 1)
        return response.json()

    def team_lookup(self):
        by_api_id = {t.api_id: t for t in Team.objects.exclude(api_id=None)}
        by_name = {}
        for team in Team.objects.all():
            by_name[normalize(TEAM_ALIASES.get(normalize(team.name), team.name))] = team
        return by_api_id, by_name

    def match_team(self, api_team, lookup):
        by_api_id, by_name = lookup
        if api_team["id"] in by_api_id:
            return by_api_id[api_team["id"]]
        api_names = {normalize(api_team.get(k) or "") for k in ("name", "shortName")}
        for our_name, team in by_name.items():
            if any(n and (n == our_name or n.startswith(our_name + " ") or n.endswith(" " + our_name))
                   for n in api_names):
                team.api_id = api_team["id"]
                team.save(update_fields=["api_id"])
                by_api_id[api_team["id"]] = team
                return team
        return None

    def fill_positions(self, players):
        players = list(players)
        # Reuse a position we already know from another season before asking the API.
        known = dict(
            PlayerRanking.objects.filter(api_id__in=[p.api_id for p in players])
            .exclude(position="").values_list("api_id", "position")
        )
        lookups = [p for p in players if p.api_id not in known]
        if lookups:
            self.stdout.write(f"Looking up positions for {len(lookups)} players...")
        for player in players:
            if player.api_id in known:
                player.position = known[player.api_id]
            else:
                person = self.get(f"/persons/{player.api_id}")
                player.position = map_position(person.get("position") or person.get("section"))
            player.save(update_fields=["position", "updated_at"])

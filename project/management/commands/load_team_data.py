from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from project.models import Team, TeamStatistic, ChampionsLeagueMatch, CLRecord

class Command(BaseCommand):
    help = 'Loads sample team data including coaches, CL records, and recent matches'

    def handle(self, *args, **options):
        # Sample data for popular teams
        teams_data = {
            'Real Madrid': {
                'coach': 'Carlo Ancelotti',
                'ucl_titles': 15,
                'ucl_finals': 18,
                'founded_year': 1902,
                'stadium_name': 'Santiago Bernabéu',
                'stadium_capacity': 81044,
                'cl_records': [
                    {'season': '2024-25', 'wins': 4, 'draws': 1, 'losses': 1, 'goals_for': 12, 'goals_against': 5, 'stage_reached': 'Round of 16'},
                    {'season': '2023-24', 'wins': 9, 'draws': 3, 'losses': 1, 'goals_for': 28, 'goals_against': 12, 'stage_reached': 'Champions'},
                    {'season': '2022-23', 'wins': 8, 'draws': 2, 'losses': 3, 'goals_for': 26, 'goals_against': 14, 'stage_reached': 'Semi Finals'},
                    {'season': '2021-22', 'wins': 9, 'draws': 0, 'losses': 4, 'goals_for': 28, 'goals_against': 14, 'stage_reached': 'Champions'},
                    {'season': '2020-21', 'wins': 6, 'draws': 2, 'losses': 2, 'goals_for': 19, 'goals_against': 11, 'stage_reached': 'Semi Finals'},
                ],
                'recent_matches': [
                    {'opponent': 'Bayern Munich', 'score_a': 2, 'score_b': 1, 'scorers_a': 'Vinicius Jr, Rodrygo', 'scorers_b': 'Kane', 'stage': 'R16', 'days_ago': 15},
                    {'opponent': 'PSG', 'score_a': 3, 'score_b': 1, 'scorers_a': 'Benzema, Vinicius Jr, Modric', 'scorers_b': 'Mbappé', 'stage': 'GROUP', 'days_ago': 30},
                    {'opponent': 'Manchester City', 'score_a': 1, 'score_b': 1, 'scorers_a': 'Rodrygo', 'scorers_b': 'Haaland', 'stage': 'GROUP', 'days_ago': 45},
                ]
            },
            'Barcelona': {
                'coach': 'Xavi',
                'ucl_titles': 5,
                'ucl_finals': 8,
                'founded_year': 1899,
                'stadium_name': 'Camp Nou',
                'stadium_capacity': 99354,
                'cl_records': [
                    {'season': '2024-25', 'wins': 3, 'draws': 2, 'losses': 1, 'goals_for': 10, 'goals_against': 6, 'stage_reached': 'Round of 16'},
                    {'season': '2023-24', 'wins': 5, 'draws': 2, 'losses': 3, 'goals_for': 18, 'goals_against': 15, 'stage_reached': 'Quarter Finals'},
                    {'season': '2022-23', 'wins': 4, 'draws': 2, 'losses': 2, 'goals_for': 15, 'goals_against': 10, 'stage_reached': 'Group Stage'},
                    {'season': '2021-22', 'wins': 2, 'draws': 1, 'losses': 3, 'goals_for': 8, 'goals_against': 12, 'stage_reached': 'Group Stage'},
                    {'season': '2020-21', 'wins': 5, 'draws': 1, 'losses': 2, 'goals_for': 18, 'goals_against': 8, 'stage_reached': 'Round of 16'},
                ],
                'recent_matches': [
                    {'opponent': 'Napoli', 'score_a': 2, 'score_b': 0, 'scorers_a': 'Lewandowski, Pedri', 'scorers_b': '', 'stage': 'R16', 'days_ago': 20},
                    {'opponent': 'Porto', 'score_a': 1, 'score_b': 1, 'scorers_a': 'Lewandowski', 'scorers_b': 'Taremi', 'stage': 'GROUP', 'days_ago': 35},
                    {'opponent': 'Shakhtar', 'score_a': 3, 'score_b': 1, 'scorers_a': 'Lewandowski, Gavi, Pedri', 'scorers_b': 'Mudryk', 'stage': 'GROUP', 'days_ago': 50},
                ]
            },
            'Manchester City': {
                'coach': 'Pep Guardiola',
                'ucl_titles': 1,
                'ucl_finals': 2,
                'founded_year': 1880,
                'stadium_name': 'Etihad Stadium',
                'stadium_capacity': 53400,
                'cl_records': [
                    {'season': '2024-25', 'wins': 5, 'draws': 1, 'losses': 0, 'goals_for': 16, 'goals_against': 4, 'stage_reached': 'Round of 16'},
                    {'season': '2023-24', 'wins': 8, 'draws': 3, 'losses': 2, 'goals_for': 27, 'goals_against': 12, 'stage_reached': 'Quarter Finals'},
                    {'season': '2022-23', 'wins': 8, 'draws': 5, 'losses': 0, 'goals_for': 32, 'goals_against': 5, 'stage_reached': 'Champions'},
                    {'season': '2021-22', 'wins': 7, 'draws': 2, 'losses': 2, 'goals_for': 29, 'goals_against': 11, 'stage_reached': 'Semi Finals'},
                    {'season': '2020-21', 'wins': 7, 'draws': 0, 'losses': 1, 'goals_for': 25, 'goals_against': 4, 'stage_reached': 'Final'},
                ],
                'recent_matches': [
                    {'opponent': 'RB Leipzig', 'score_a': 3, 'score_b': 1, 'scorers_a': 'Haaland (2), Foden', 'scorers_b': 'Openda', 'stage': 'GROUP', 'days_ago': 25},
                    {'opponent': 'Young Boys', 'score_a': 4, 'score_b': 0, 'scorers_a': 'Haaland (2), Álvarez, Foden', 'scorers_b': '', 'stage': 'GROUP', 'days_ago': 40},
                    {'opponent': 'Red Star', 'score_a': 2, 'score_b': 1, 'scorers_a': 'Haaland, Rodri', 'scorers_b': 'Katai', 'stage': 'GROUP', 'days_ago': 55},
                ]
            },
            'Bayern Munich': {
                'coach': 'Thomas Tuchel',
                'ucl_titles': 6,
                'ucl_finals': 11,
                'founded_year': 1900,
                'stadium_name': 'Allianz Arena',
                'stadium_capacity': 75000,
                'cl_records': [
                    {'season': '2024-25', 'wins': 4, 'draws': 2, 'losses': 0, 'goals_for': 14, 'goals_against': 6, 'stage_reached': 'Round of 16'},
                    {'season': '2023-24', 'wins': 7, 'draws': 2, 'losses': 2, 'goals_for': 24, 'goals_against': 13, 'stage_reached': 'Semi Finals'},
                    {'season': '2022-23', 'wins': 7, 'draws': 2, 'losses': 1, 'goals_for': 21, 'goals_against': 8, 'stage_reached': 'Quarter Finals'},
                    {'season': '2021-22', 'wins': 8, 'draws': 0, 'losses': 1, 'goals_for': 31, 'goals_against': 8, 'stage_reached': 'Quarter Finals'},
                    {'season': '2020-21', 'wins': 9, 'draws': 1, 'losses': 1, 'goals_for': 27, 'goals_against': 8, 'stage_reached': 'Champions'},
                ],
                'recent_matches': [
                    {'opponent': 'Real Madrid', 'score_a': 1, 'score_b': 2, 'scorers_a': 'Kane', 'scorers_b': 'Vinicius Jr, Rodrygo', 'stage': 'R16', 'days_ago': 15},
                    {'opponent': 'Copenhagen', 'score_a': 2, 'score_b': 1, 'scorers_a': 'Kane, Musiala', 'scorers_b': 'Elyounoussi', 'stage': 'GROUP', 'days_ago': 30},
                    {'opponent': 'Galatasaray', 'score_a': 3, 'score_b': 1, 'scorers_a': 'Kane (2), Coman', 'scorers_b': 'Icardi', 'stage': 'GROUP', 'days_ago': 45},
                ]
            },
            'PSG': {
                'coach': 'Luis Enrique',
                'ucl_titles': 0,
                'ucl_finals': 1,
                'founded_year': 1970,
                'stadium_name': 'Parc des Princes',
                'stadium_capacity': 47929,
                'cl_records': [
                    {'season': '2024-25', 'wins': 3, 'draws': 2, 'losses': 1, 'goals_for': 11, 'goals_against': 7, 'stage_reached': 'Round of 16'},
                    {'season': '2023-24', 'wins': 4, 'draws': 2, 'losses': 2, 'goals_for': 15, 'goals_against': 9, 'stage_reached': 'Semi Finals'},
                    {'season': '2022-23', 'wins': 4, 'draws': 2, 'losses': 2, 'goals_for': 16, 'goals_against': 10, 'stage_reached': 'Round of 16'},
                    {'season': '2021-22', 'wins': 3, 'draws': 2, 'losses': 3, 'goals_for': 13, 'goals_against': 13, 'stage_reached': 'Round of 16'},
                    {'season': '2020-21', 'wins': 6, 'draws': 1, 'losses': 3, 'goals_for': 22, 'goals_against': 10, 'stage_reached': 'Semi Finals'},
                ],
                'recent_matches': [
                    {'opponent': 'Real Madrid', 'score_a': 1, 'score_b': 3, 'scorers_a': 'Mbappé', 'scorers_b': 'Benzema, Vinicius Jr, Modric', 'stage': 'GROUP', 'days_ago': 30},
                    {'opponent': 'Newcastle', 'score_a': 2, 'score_b': 1, 'scorers_a': 'Mbappé, Dembélé', 'scorers_b': 'Isak', 'stage': 'GROUP', 'days_ago': 45},
                    {'opponent': 'AC Milan', 'score_a': 1, 'score_b': 1, 'scorers_a': 'Mbappé', 'scorers_b': 'Giroud', 'stage': 'GROUP', 'days_ago': 60},
                ]
            },
        }

        # Add more teams
        additional_teams = {
            'Atletico Madrid': {'coach': 'Diego Simeone', 'ucl_titles': 0, 'ucl_finals': 3, 'founded_year': 1903, 'stadium_name': 'Wanda Metropolitano', 'stadium_capacity': 67703},
            'Borussia Dortmund': {'coach': 'Edin Terzić', 'ucl_titles': 1, 'ucl_finals': 2, 'founded_year': 1909, 'stadium_name': 'Signal Iduna Park', 'stadium_capacity': 81365},
            'Chelsea': {'coach': 'Mauricio Pochettino', 'ucl_titles': 2, 'ucl_finals': 3, 'founded_year': 1905, 'stadium_name': 'Stamford Bridge', 'stadium_capacity': 40341},
            'Tottenham': {'coach': 'Ange Postecoglou', 'ucl_titles': 0, 'ucl_finals': 1, 'founded_year': 1882, 'stadium_name': 'Tottenham Hotspur Stadium', 'stadium_capacity': 62850},
            'Juventus': {'coach': 'Massimiliano Allegri', 'ucl_titles': 2, 'ucl_finals': 9, 'founded_year': 1897, 'stadium_name': 'Allianz Stadium', 'stadium_capacity': 41507},
        }

        current_season = '2024-25'
        current_date = timezone.now()

        for team_name, data in teams_data.items():
            try:
                team = Team.objects.get(name=team_name)
                
                # Update or create statistics
                stats, created = TeamStatistic.objects.get_or_create(
                    team=team,
                    defaults={
                        'coach': data['coach'],
                        'ucl_titles': data['ucl_titles'],
                        'ucl_finals': data['ucl_finals'],
                        'founded_year': data['founded_year'],
                        'stadium_name': data['stadium_name'],
                        'stadium_capacity': data['stadium_capacity'],
                    }
                )
                if not created:
                    stats.coach = data['coach']
                    stats.save()
                
                # Create CL records
                for record_data in data['cl_records']:
                    CLRecord.objects.update_or_create(
                        team=team,
                        season=record_data['season'],
                        defaults=record_data
                    )
                
                # Create recent matches
                for match_data in data['recent_matches']:
                    # Find opponent team
                    opponent = Team.objects.filter(name__icontains=match_data['opponent']).first()
                    if not opponent:
                        # Try to find by partial match
                        for t in Team.objects.all():
                            if match_data['opponent'].split()[0] in t.name or t.name.split()[0] in match_data['opponent']:
                                opponent = t
                                break
                    
                    if opponent:
                        match_date = current_date - timedelta(days=match_data['days_ago'])
                        # Determine which team is team_a (home) - alternate
                        if team.id < opponent.id:
                            team_a, team_b = team, opponent
                            score_a, score_b = match_data['score_a'], match_data['score_b']
                            scorers_a, scorers_b = match_data['scorers_a'], match_data['scorers_b']
                        else:
                            team_a, team_b = opponent, team
                            score_a, score_b = match_data['score_b'], match_data['score_a']
                            scorers_a, scorers_b = match_data['scorers_b'], match_data['scorers_a']
                        
                        ChampionsLeagueMatch.objects.update_or_create(
                            team_a=team_a,
                            team_b=team_b,
                            match_date=match_date,
                            season=current_season,
                            defaults={
                                'tournament_stage': match_data['stage'],
                                'team_a_score': score_a,
                                'team_b_score': score_b,
                                'team_a_scorers': scorers_a,
                                'team_b_scorers': scorers_b,
                            }
                        )
                
                self.stdout.write(self.style.SUCCESS(f'✓ Loaded data for {team_name}'))
            except Team.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'⚠ Team {team_name} not found in database'))
        
        # Handle additional teams with basic data
        for team_name, data in additional_teams.items():
            try:
                team = Team.objects.get(name=team_name)
                stats, created = TeamStatistic.objects.get_or_create(
                    team=team,
                    defaults=data
                )
                if not created:
                    for key, value in data.items():
                        setattr(stats, key, value)
                    stats.save()
                self.stdout.write(self.style.SUCCESS(f'✓ Loaded basic data for {team_name}'))
            except Team.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'⚠ Team {team_name} not found in database'))

        self.stdout.write(self.style.SUCCESS('\n✓ Team data loading complete!'))


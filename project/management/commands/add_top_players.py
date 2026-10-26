"""
Management command to add top Champions League players
"""
from django.core.management.base import BaseCommand
from project.models import PlayerRanking, Team

class Command(BaseCommand):
    help = 'Adds 7 top Champions League players to the database'

    def handle(self, *args, **options):
        # Top 7 players with realistic G+A per 90 stats
        players_data = [
            {
                'player_name': 'Kylian Mbappé',
                'team_name': 'PSG',
                'rank_int': 6,
                'position': 'FWD',
                'ga_per_90': 1.45,  # Elite forward stats
            },
            {
                'player_name': 'Erling Haaland',
                'team_name': 'Manchester City',
                'rank_int': 7,
                'position': 'FWD',
                'ga_per_90': 1.52,  # Top striker
            },
            {
                'player_name': 'Mohamed Salah',
                'team_name': 'Liverpool',
                'rank_int': 8,
                'position': 'FWD',
                'ga_per_90': 1.38,  # Consistent winger
            },
            {
                'player_name': 'Jude Bellingham',
                'team_name': 'Real Madrid',
                'rank_int': 9,
                'position': 'MID',
                'ga_per_90': 0.95,  # Attacking midfielder
            },
            {
                'player_name': 'Harry Kane',
                'team_name': 'Bayern Munich',
                'rank_int': 10,
                'position': 'FWD',
                'ga_per_90': 1.42,  # Elite striker
            },
            {
                'player_name': 'Lamine Yamal',
                'team_name': 'Barcelona',
                'rank_int': 11,
                'position': 'FWD',
                'ga_per_90': 1.15,  # Young talent
            },
            {
                'player_name': 'Pedri',
                'team_name': 'Barcelona',
                'rank_int': 12,
                'position': 'MID',
                'ga_per_90': 0.72,  # Creative midfielder
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for player_data in players_data:
            team_name = player_data.pop('team_name')
            
            try:
                team = Team.objects.get(name=team_name)
            except Team.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'Team "{team_name}" not found. Skipping {player_data["player_name"]}')
                )
                continue
            
            player, created = PlayerRanking.objects.update_or_create(
                player_name=player_data['player_name'],
                team=team,
                defaults={
                    'rank_int': player_data['rank_int'],
                    'position': player_data['position'],
                    'ga_per_90': player_data['ga_per_90'],
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created: {player.player_name} ({team.name})')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Updated: {player.player_name} ({team.name})')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nCompleted! Created {created_count} players, updated {updated_count} players.'
            )
        )


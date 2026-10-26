"""
Management command to fix player rankings and set Harry Kane as #1
"""
from django.core.management.base import BaseCommand
from project.models import PlayerRanking, Team

class Command(BaseCommand):
    help = 'Fixes player rankings so Harry Kane is #1 and list starts from 1'

    def handle(self, *args, **options):
        # Define the correct order with Harry Kane as #1
        players_order = [
            {'player_name': 'Harry Kane', 'team_name': 'Bayern Munich', 'rank': 1},
            {'player_name': 'Kylian Mbappé', 'team_name': 'PSG', 'rank': 2},
            {'player_name': 'Erling Haaland', 'team_name': 'Manchester City', 'rank': 3},
            {'player_name': 'Mohamed Salah', 'team_name': 'Liverpool', 'rank': 4},
            {'player_name': 'Jude Bellingham', 'team_name': 'Real Madrid', 'rank': 5},
            {'player_name': 'Lamine Yamal', 'team_name': 'Barcelona', 'rank': 6},
            {'player_name': 'Pedri', 'team_name': 'Barcelona', 'rank': 7},
        ]
        
        # Get all existing players first to see what we have
        all_players = PlayerRanking.objects.all()
        self.stdout.write(f'Found {all_players.count()} existing players')
        
        updated_count = 0
        created_count = 0
        
        for player_data in players_order:
            team_name = player_data['team_name']
            player_name = player_data['player_name']
            new_rank = player_data['rank']
            
            try:
                team = Team.objects.get(name=team_name)
            except Team.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'Team "{team_name}" not found. Skipping {player_name}')
                )
                continue
            
            # Try to find existing player
            try:
                player = PlayerRanking.objects.get(player_name=player_name, team=team)
                old_rank = player.rank_int
                player.rank_int = new_rank
                player.save()
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Updated: {player_name} ({team.name}) - Rank {old_rank} → {new_rank}')
                )
            except PlayerRanking.DoesNotExist:
                # Player doesn't exist, but we'll skip creation here since we just want to fix ranks
                self.stdout.write(
                    self.style.WARNING(f'Player "{player_name}" not found. Run add_top_players first.')
                )
        
        # Also update any other players to have ranks starting from where we left off
        # Get all players not in our list and renumber them
        existing_player_names = [p['player_name'] for p in players_order]
        other_players = PlayerRanking.objects.exclude(player_name__in=existing_player_names).order_by('rank_int')
        
        next_rank = len(players_order) + 1
        for player in other_players:
            old_rank = player.rank_int
            player.rank_int = next_rank
            player.save()
            self.stdout.write(
                self.style.SUCCESS(f'Renumbered: {player.player_name} ({player.team.name}) - Rank {old_rank} → {next_rank}')
            )
            next_rank += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nCompleted! Updated {updated_count} players. Harry Kane is now #1.'
            )
        )


from django.core.management.base import BaseCommand
from project.models import Team


class Command(BaseCommand):
    help = 'Adds the 5 new teams: Atletico Madrid, Borussia Dortmund, Chelsea, Tottenham, and Juventus'

    def handle(self, *args, **options):
        # Teams to add with their information
        teams_data = [
            {
                'name': 'Atletico Madrid',
                'country': 'Spain',
                'league': 'La Liga',
                'logo_url': 'https://logos-world.net/wp-content/uploads/2020/06/Atletico-Madrid-Logo.png'
            },
            {
                'name': 'Borussia Dortmund',
                'country': 'Germany',
                'league': 'Bundesliga',
                'logo_url': 'https://logos-world.net/wp-content/uploads/2020/06/Borussia-Dortmund-Logo.png'
            },
            {
                'name': 'Chelsea',
                'country': 'England',
                'league': 'Premier League',
                'logo_url': 'https://logos-world.net/wp-content/uploads/2020/06/Chelsea-Logo.png'
            },
            {
                'name': 'Tottenham',
                'country': 'England',
                'league': 'Premier League',
                'logo_url': 'https://logos-world.net/wp-content/uploads/2020/06/Tottenham-Hotspur-Logo.png'
            },
            {
                'name': 'Juventus',
                'country': 'Italy',
                'league': 'Serie A',
                'logo_url': 'https://logos-world.net/wp-content/uploads/2020/06/Juventus-Logo.png'
            },
        ]

        # Add teams (skip if they already exist)
        created_count = 0
        updated_count = 0
        for team_data in teams_data:
            team, created = Team.objects.get_or_create(
                name=team_data['name'],
                defaults={
                    'country': team_data['country'],
                    'league': team_data['league'],
                    'logo_url': team_data['logo_url']
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created team: {team.name}'))
            else:
                # Update existing team with logo if it doesn't have one
                if not team.logo_url:
                    team.logo_url = team_data['logo_url']
                    team.country = team_data['country']
                    team.league = team_data['league']
                    team.save()
                    updated_count += 1
                    self.stdout.write(self.style.WARNING(f'↻ Updated team: {team.name}'))
                else:
                    self.stdout.write(self.style.NOTICE(f'○ Team already exists: {team.name}'))

        self.stdout.write(self.style.SUCCESS(f'\n✓ Created {created_count} new teams'))
        if updated_count > 0:
            self.stdout.write(self.style.WARNING(f'↻ Updated {updated_count} existing teams'))
        self.stdout.write(self.style.SUCCESS(f'Total teams in database: {Team.objects.count()}'))


# Run this in Django shell: python manage.py shell
# Then: exec(open('project/load_teams.py').read())

from project.models import Team

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
        print(f"Created team: {team.name}")
    else:
        # Update existing team with logo if it doesn't have one
        if not team.logo_url:
            team.logo_url = team_data['logo_url']
            team.save()
            print(f"Updated logo for: {team.name}")
        else:
            print(f"Team already exists: {team.name}")

print(f"\nTotal teams in database: {Team.objects.count()}")


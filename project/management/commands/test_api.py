from django.core.management.base import BaseCommand
from django.conf import settings
from project.api_service import get_team_matches_from_api, get_team_cl_record_from_api, API_KEY, REQUESTS_AVAILABLE

class Command(BaseCommand):
    help = 'Test the Football Data API connection and fetch sample data'

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write("Testing Football Data API Connection")
        self.stdout.write("=" * 60)
        
        # Check if requests is available
        if not REQUESTS_AVAILABLE:
            self.stdout.write(self.style.ERROR("❌ 'requests' module is not installed!"))
            self.stdout.write(self.style.WARNING("Install it with: pip install requests"))
            return
        
        self.stdout.write(self.style.SUCCESS("✓ 'requests' module is available"))
        
        # Check API key
        if not API_KEY:
            self.stdout.write(self.style.ERROR("❌ API key is not set in settings.py"))
            self.stdout.write(self.style.WARNING("Set FOOTBALL_DATA_API_KEY in cs412/settings.py"))
            return
        
        self.stdout.write(self.style.SUCCESS(f"✓ API key is set: {API_KEY[:10]}..."))
        
        # Test API connection
        try:
            import requests
            headers = {'X-Auth-Token': API_KEY}
            test_url = 'https://api.football-data.org/v4/competitions/2001'
            
            self.stdout.write("\nTesting API connection...")
            response = requests.get(test_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.stdout.write(self.style.SUCCESS(f"✓ API connection successful!"))
                self.stdout.write(f"  Competition: {data.get('name', 'N/A')}")
                self.stdout.write(f"  Current Season: {data.get('currentSeason', {}).get('startDate', 'N/A')}")
            elif response.status_code == 429:
                self.stdout.write(self.style.ERROR("❌ API rate limit exceeded. Please wait a moment and try again."))
            elif response.status_code == 401:
                self.stdout.write(self.style.ERROR("❌ API key is invalid or unauthorized"))
            else:
                self.stdout.write(self.style.ERROR(f"❌ API returned status {response.status_code}"))
                self.stdout.write(f"  Response: {response.text[:200]}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error connecting to API: {e}"))
            return
        
        # Test fetching matches for Real Madrid
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("Testing Match Data Fetching")
        self.stdout.write("=" * 60)
        
        test_team = "Real Madrid"
        self.stdout.write(f"\nFetching matches for {test_team}...")
        matches = get_team_matches_from_api(test_team)
        
        if matches:
            self.stdout.write(self.style.SUCCESS(f"✓ Found {len(matches)} matches"))
            for i, match in enumerate(matches[:3], 1):
                self.stdout.write(f"\n  Match {i}:")
                self.stdout.write(f"    {match.get('home_team', 'N/A')} {match.get('home_score', 0)} - {match.get('away_score', 0)} {match.get('away_team', 'N/A')}")
                self.stdout.write(f"    Date: {match.get('date', 'N/A')}")
                self.stdout.write(f"    Stage: {match.get('stage', 'N/A')}")
        else:
            self.stdout.write(self.style.WARNING("⚠ No matches found (may be using database fallback)"))
        
        # Test fetching CL records
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("Testing CL Record Fetching")
        self.stdout.write("=" * 60)
        
        self.stdout.write(f"\nFetching CL records for {test_team}...")
        records = get_team_cl_record_from_api(test_team)
        
        if records:
            self.stdout.write(self.style.SUCCESS(f"✓ Found {len(records)} season records"))
            for record in records[:3]:
                self.stdout.write(f"\n  {record.get('season', 'N/A')}:")
                self.stdout.write(f"    Record: {record.get('wins', 0)}-{record.get('draws', 0)}-{record.get('losses', 0)}")
                self.stdout.write(f"    Goals: {record.get('goals_for', 0)}:{record.get('goals_against', 0)}")
                self.stdout.write(f"    Stage: {record.get('stage_reached', 'N/A')}")
        else:
            self.stdout.write(self.style.WARNING("⚠ No records found (may be using database fallback)"))
        
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("API Test Complete!"))
        self.stdout.write("=" * 60)


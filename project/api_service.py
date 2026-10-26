"""
API Service for fetching up-to-date Champions League data
Uses football-data.org free API (requires free API key)
"""
import json
from datetime import datetime, timedelta
from django.core.cache import cache
from django.conf import settings
from django.db.models import Q
from .models import Team, ChampionsLeagueMatch, CLRecord
from .cl_records_data import CL_RECORDS_DATA

# Try to import requests, but make it optional
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    requests = None

# Free API key - user should get their own from https://www.football-data.org/
# For now, we'll use a fallback approach
API_KEY = getattr(settings, 'FOOTBALL_DATA_API_KEY', None)
API_BASE_URL = 'https://api.football-data.org/v4'

# Team name mapping for API compatibility
TEAM_NAME_MAPPING = {
    'Real Madrid': 'Real Madrid',
    'Barcelona': 'FC Barcelona',
    'Manchester City': 'Manchester City FC',
    'Bayern Munich': 'FC Bayern München',
    'PSG': 'Paris Saint-Germain',
    'Atletico Madrid': 'Atlético Madrid',
    'Borussia Dortmund': 'Borussia Dortmund',
    'Chelsea': 'Chelsea FC',
    'Tottenham': 'Tottenham Hotspur',
    'Juventus': 'Juventus FC',
}


def get_team_matches_from_api(team_name, season=None):
    """
    Fetch recent Champions League matches for a team from API
    Falls back to database if API is unavailable
    """
    if not API_KEY or not REQUESTS_AVAILABLE:
        # Fallback to database
        return get_team_matches_from_db(team_name, season)
    
    try:
        # Create cache key without spaces or special chars
        safe_team_name = team_name.replace(' ', '_').replace('/', '_')
        cache_key = f'ucl_matches_{safe_team_name}_{season or "current"}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        headers = {'X-Auth-Token': API_KEY}
        
        # Get current season if not provided
        if not season:
            current_year = datetime.now().year
            season = f"{current_year}-{current_year + 1}"
        
        season_year = int(season.split('-')[0])
        
        # Get Champions League competition ID (2001 is UCL)
        matches_url = f"{API_BASE_URL}/competitions/2001/matches"
        params = {'season': season_year}
        
        print(f"Fetching matches from API for season {season_year}...")
        response = requests.get(matches_url, headers=headers, params=params, timeout=10)
        print(f"API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            all_matches = data.get('matches', [])
            print(f"Total matches returned: {len(all_matches)}")
            matches = []
            
            # Filter matches for this team - try multiple name variations
            api_team_name = TEAM_NAME_MAPPING.get(team_name, team_name)
            team_variations = [team_name, api_team_name]
            # Add partial matches
            if ' ' in team_name:
                parts = team_name.split()
                team_variations.append(parts[0])
                if len(parts) > 1:
                    team_variations.append(parts[-1])
            
            # Normalize team name for comparison (remove common suffixes)
            def normalize_team_name(name):
                if not name:
                    return ''
                name = name.upper()
                # Remove common suffixes
                for suffix in [' CF', ' FC', ' FC.', ' CF.', ' FOOTBALL CLUB']:
                    if name.endswith(suffix):
                        name = name[:-len(suffix)].strip()
                return name
            
            normalized_team = normalize_team_name(team_name)
            
            for match in all_matches:
                home_team_obj = match.get('homeTeam', {})
                away_team_obj = match.get('awayTeam', {})
                home_team = home_team_obj.get('name', '') if home_team_obj else ''
                away_team = away_team_obj.get('name', '') if away_team_obj else ''
                
                # Skip if team names are missing
                if not home_team or not away_team:
                    continue
                
                # Check if this team is in the match (use normalized names for better matching)
                team_found = False
                normalized_home = normalize_team_name(home_team)
                normalized_away = normalize_team_name(away_team)
                
                # Check exact match or partial match
                if (normalized_team in normalized_home or normalized_team in normalized_away or
                    normalized_home in normalized_team or normalized_away in normalized_team):
                    team_found = True
                else:
                    # Try variations
                    for variation in team_variations:
                        if variation:
                            norm_var = normalize_team_name(variation)
                            if (norm_var in normalized_home or norm_var in normalized_away or
                                normalized_home in norm_var or normalized_away in norm_var):
                                team_found = True
                                break
                
                if team_found:
                    # Get scores
                    score_data = match.get('score', {})
                    full_time = score_data.get('fullTime', {})
                    home_score = full_time.get('home')
                    away_score = full_time.get('away')
                    
                    # Get scorers if available
                    home_scorers = []
                    away_scorers = []
                    goals = match.get('goals', [])
                    if goals:
                        for goal in goals:
                            goal_team = goal.get('team', {})
                            if goal_team and goal_team.get('name') == home_team:
                                scorer_obj = goal.get('scorer', {})
                                scorer = scorer_obj.get('name', 'Unknown') if scorer_obj else 'Unknown'
                                minute = goal.get('minute', '')
                                if minute:
                                    home_scorers.append(f"{scorer} ({minute}')")
                                else:
                                    home_scorers.append(scorer)
                            elif goal_team and goal_team.get('name') == away_team:
                                scorer_obj = goal.get('scorer', {})
                                scorer = scorer_obj.get('name', 'Unknown') if scorer_obj else 'Unknown'
                                minute = goal.get('minute', '')
                                if minute:
                                    away_scorers.append(f"{scorer} ({minute}')")
                                else:
                                    away_scorers.append(scorer)
                    
                    # Parse date
                    match_date_str = match.get('utcDate', '')
                    try:
                        if match_date_str:
                            # Parse ISO format date (handle both with and without timezone)
                            if 'Z' in match_date_str:
                                # Remove Z and add +00:00 for timezone
                                match_date_str = match_date_str.replace('Z', '+00:00')
                            # Parse ISO format
                            if '+' in match_date_str or match_date_str.count('-') >= 3:
                                match_date = datetime.fromisoformat(match_date_str)
                            else:
                                # Fallback: try basic parsing
                                match_date = datetime.strptime(match_date_str[:19], '%Y-%m-%dT%H:%M:%S')
                        else:
                            match_date = datetime.now()
                    except Exception as e:
                        print(f"Date parsing error for '{match_date_str}': {e}")
                        match_date = datetime.now()
                    
                    # Map stage
                    stage = match.get('stage', 'GROUP_STAGE')
                    stage_map = {
                        'GROUP_STAGE': 'GROUP',
                        'LAST_16': 'R16',
                        'QUARTER_FINALS': 'QF',
                        'SEMI_FINALS': 'SF',
                        'FINAL': 'FINAL',
                    }
                    stage = stage_map.get(stage, 'GROUP')
                    
                    match_data = {
                        'date': match_date,
                        'home_team': home_team,
                        'away_team': away_team,
                        'home_score': home_score if home_score is not None else 0,
                        'away_score': away_score if away_score is not None else 0,
                        'stage': stage,
                        'status': match.get('status', 'FINISHED'),
                        'scorers': {
                            'home': ', '.join(home_scorers) if home_scorers else '',
                            'away': ', '.join(away_scorers) if away_scorers else '',
                        }
                    }
                    matches.append(match_data)
            
            # Sort by date (most recent first) and limit to 10
            matches.sort(key=lambda x: x['date'], reverse=True)
            matches = matches[:10]
            
            print(f"Found {len(matches)} matches for {team_name}")
            
            # Cache for 1 hour
            cache.set(cache_key, matches, 3600)
            return matches
        else:
            print(f"API returned status {response.status_code}: {response.text[:200]}")
            return get_team_matches_from_db(team_name, season)
            
    except Exception as e:
        print(f"API Error: {e}")
        import traceback
        traceback.print_exc()
        return get_team_matches_from_db(team_name, season)


def get_all_recent_matches_from_api(limit=50):
    """
    Fetch all recent Champions League matches from API
    Returns matches for all teams, sorted by date (most recent first)
    """
    if not API_KEY or not REQUESTS_AVAILABLE:
        return get_all_recent_matches_from_db(limit)
    
    try:
        cache_key = 'ucl_all_recent_matches'
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        headers = {'X-Auth-Token': API_KEY}
        current_year = datetime.now().year
        season_year = current_year
        
        # Get Champions League competition ID (2001 is UCL)
        matches_url = f"{API_BASE_URL}/competitions/2001/matches"
        params = {'season': season_year}
        
        print(f"Fetching all recent matches from API for season {season_year}...")
        response = requests.get(matches_url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            all_matches = data.get('matches', [])
            print(f"Total matches returned: {len(all_matches)}")
            matches = []
            
            # Normalize team name for comparison
            def normalize_team_name(name):
                if not name:
                    return ''
                name = name.upper()
                for suffix in [' CF', ' FC', ' FC.', ' CF.', ' FOOTBALL CLUB']:
                    if name.endswith(suffix):
                        name = name[:-len(suffix)].strip()
                return name
            
            for match in all_matches:
                home_team_obj = match.get('homeTeam', {})
                away_team_obj = match.get('awayTeam', {})
                home_team = home_team_obj.get('name', '') if home_team_obj else ''
                away_team = away_team_obj.get('name', '') if away_team_obj else ''
                
                if not home_team or not away_team:
                    continue
                
                # Get scores
                score_data = match.get('score', {})
                full_time = score_data.get('fullTime', {})
                home_score = full_time.get('home')
                away_score = full_time.get('away')
                
                # Skip if match hasn't been played yet
                if home_score is None or away_score is None:
                    continue
                
                # Get scorers if available
                home_scorers = []
                away_scorers = []
                goals = match.get('goals', [])
                if goals:
                    for goal in goals:
                        goal_team = goal.get('team', {})
                        if goal_team and goal_team.get('name') == home_team:
                            scorer_obj = goal.get('scorer', {})
                            scorer = scorer_obj.get('name', 'Unknown') if scorer_obj else 'Unknown'
                            minute = goal.get('minute', '')
                            if minute:
                                home_scorers.append(f"{scorer} ({minute}')")
                            else:
                                home_scorers.append(scorer)
                        elif goal_team and goal_team.get('name') == away_team:
                            scorer_obj = goal.get('scorer', {})
                            scorer = scorer_obj.get('name', 'Unknown') if scorer_obj else 'Unknown'
                            minute = goal.get('minute', '')
                            if minute:
                                away_scorers.append(f"{scorer} ({minute}')")
                            else:
                                away_scorers.append(scorer)
                
                # Parse date
                match_date_str = match.get('utcDate', '')
                try:
                    if match_date_str:
                        if 'Z' in match_date_str:
                            match_date_str = match_date_str.replace('Z', '+00:00')
                        if '+' in match_date_str or match_date_str.count('-') >= 3:
                            match_date = datetime.fromisoformat(match_date_str)
                        else:
                            match_date = datetime.strptime(match_date_str[:19], '%Y-%m-%dT%H:%M:%S')
                    else:
                        match_date = datetime.now()
                except Exception as e:
                    print(f"Date parsing error for '{match_date_str}': {e}")
                    match_date = datetime.now()
                
                # Map stage
                stage = match.get('stage', 'GROUP_STAGE')
                stage_map = {
                    'GROUP_STAGE': 'GROUP',
                    'LAST_16': 'R16',
                    'QUARTER_FINALS': 'QF',
                    'SEMI_FINALS': 'SF',
                    'FINAL': 'FINAL',
                }
                stage = stage_map.get(stage, 'GROUP')
                
                match_data = {
                    'date': match_date,
                    'home_team': home_team,
                    'away_team': away_team,
                    'home_score': home_score if home_score is not None else 0,
                    'away_score': away_score if away_score is not None else 0,
                    'stage': stage,
                    'status': match.get('status', 'FINISHED'),
                    'scorers': {
                        'home': ', '.join(home_scorers) if home_scorers else '',
                        'away': ', '.join(away_scorers) if away_scorers else '',
                    }
                }
                matches.append(match_data)
            
            # Sort by date (most recent first) and limit
            matches.sort(key=lambda x: x['date'], reverse=True)
            matches = matches[:limit]
            
            print(f"Found {len(matches)} recent matches")
            
            # Cache for 1 hour
            cache.set(cache_key, matches, 3600)
            return matches
        else:
            print(f"API returned status {response.status_code}: {response.text[:200]}")
            return get_all_recent_matches_from_db(limit)
            
    except Exception as e:
        print(f"API Error: {e}")
        import traceback
        traceback.print_exc()
        return get_all_recent_matches_from_db(limit)


def get_all_recent_matches_from_db(limit=50):
    """Fallback: Get all recent matches from database"""
    try:
        from datetime import datetime
        current_year = datetime.now().year
        current_season = f"{current_year}-{current_year + 1}"
        
        matches = ChampionsLeagueMatch.objects.filter(
            season=current_season
        ).order_by('-match_date')[:limit]
        
        return [{
            'date': m.match_date,
            'home_team': m.team_a.name,
            'away_team': m.team_b.name,
            'home_score': m.team_a_score,
            'away_score': m.team_b_score,
            'stage': m.tournament_stage,
            'status': 'FINISHED',
            'scorers': {
                'home': m.team_a_scorers,
                'away': m.team_b_scorers,
            }
        } for m in matches]
    except Exception as e:
        print(f"Database error: {e}")
        return []


def get_team_matches_from_db(team_name, season=None):
    """Fallback: Get matches from database"""
    try:
        team = Team.objects.get(name=team_name)
        if not season:
            current_year = datetime.now().year
            season = f"{current_year}-{current_year + 1}"
        
        matches = ChampionsLeagueMatch.objects.filter(
            (Q(team_a=team) | Q(team_b=team)),
            season=season
        ).order_by('-match_date')[:10]
        
        return [{
            'date': m.match_date,
            'home_team': m.team_a.name,
            'away_team': m.team_b.name,
            'home_score': m.team_a_score,
            'away_score': m.team_b_score,
            'stage': m.tournament_stage,
            'scorers': {
                'home': m.team_a_scorers,
                'away': m.team_b_scorers,
            }
        } for m in matches]
    except Team.DoesNotExist:
        return []


def get_team_cl_record_from_api(team_name):
    """
    Fetch 5-year Champions League record from API
    Falls back to hardcoded data or database if API is unavailable
    """
    # Create cache key without spaces
    safe_team_name = team_name.replace(' ', '_').replace('/', '_')
    cache_key = f'ucl_record_{safe_team_name}'
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    # First, try hardcoded data (most reliable for historical records)
    if team_name in CL_RECORDS_DATA:
        records = CL_RECORDS_DATA[team_name]
        cache.set(cache_key, records, 21600)
        return records
    
    # Try API if available
    if API_KEY and REQUESTS_AVAILABLE:
        try:
            headers = {'X-Auth-Token': API_KEY}
            current_year = datetime.now().year
            records = []
            
            # Get records for last 5 years
            for i in range(5):
                season_year = current_year - i
                season = f"{season_year}-{season_year + 1}"
                
                try:
                    # Get standings for that season
                    standings_url = f"{API_BASE_URL}/competitions/2001/standings"
                    params = {'season': season_year}
                    
                    print(f"Fetching CL standings for {season}...")
                    response = requests.get(standings_url, headers=headers, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        standings = data.get('standings', [])
                        
                        # Find team in standings
                        api_team_name = TEAM_NAME_MAPPING.get(team_name, team_name)
                        team_variations = [team_name, api_team_name]
                        if ' ' in team_name:
                            parts = team_name.split()
                            team_variations.append(parts[0])
                            if len(parts) > 1:
                                team_variations.append(parts[-1])
                        
                        for group in standings:
                            table = group.get('table', [])
                            for entry in table:
                                entry_team_obj = entry.get('team', {})
                                entry_team_name = entry_team_obj.get('name', '') if entry_team_obj else ''
                                
                                if not entry_team_name:
                                    continue
                                
                                # Check if this is our team
                                team_found = False
                                for variation in team_variations:
                                    if variation and (variation in entry_team_name or entry_team_name in variation):
                                        team_found = True
                                        break
                                
                                if team_found:
                                    # Extract record data
                                    played = entry.get('playedGames', 0)
                                    wins = entry.get('won', 0)
                                    draws = entry.get('draw', 0)
                                    losses = entry.get('lost', 0)
                                    goals_for = entry.get('goalsFor', 0)
                                    goals_against = entry.get('goalsAgainst', 0)
                                    
                                    # Determine stage reached (simplified - would need to check knockout rounds)
                                    stage = 'Group Stage'
                                    if entry.get('group'):
                                        stage = f"Group {entry.get('group')}"
                                    
                                    records.append({
                                        'season': season,
                                        'wins': wins,
                                        'draws': draws,
                                        'losses': losses,
                                        'goals_for': goals_for,
                                        'goals_against': goals_against,
                                        'stage_reached': stage,
                                    })
                                    break
                    
                except Exception as e:
                    print(f"Error fetching record for {season}: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            # If we got records from API, return them
            if records:
                print(f"Found {len(records)} CL records from API for {team_name}")
                cache.set(cache_key, records, 21600)
                return records
            
        except Exception as e:
            print(f"API Error fetching CL records: {e}")
            import traceback
            traceback.print_exc()
    
    # Final fallback to database
    return get_team_cl_record_from_db(team_name)


def get_team_cl_record_from_db(team_name):
    """Fallback: Get CL records from database"""
    try:
        team = Team.objects.get(name=team_name)
        current_year = datetime.now().year
        seasons = [f"{current_year - i}-{current_year - i + 1}" for i in range(5)]
        
        records = CLRecord.objects.filter(
            team=team,
            season__in=seasons
        ).order_by('-season')
        
        return [{
            'season': r.season,
            'wins': r.wins,
            'draws': r.draws,
            'losses': r.losses,
            'goals_for': r.goals_for,
            'goals_against': r.goals_against,
            'stage_reached': r.stage_reached,
        } for r in records]
    except Team.DoesNotExist:
        return []


def sync_team_data_from_api(team_name):
    """
    Sync team data from API and update database
    This can be called periodically via a management command or cron job
    """
    if not API_KEY or not REQUESTS_AVAILABLE:
        return False
    
    try:
        # Get matches and update database
        matches = get_team_matches_from_api(team_name)
        team = Team.objects.get(name=team_name)
        
        for match_data in matches:
            # Find or create opponent team
            opponent_name = match_data['away_team'] if match_data['home_team'] == team_name else match_data['home_team']
            opponent, _ = Team.objects.get_or_create(
                name=opponent_name,
                defaults={'country': 'Unknown', 'league': 'Unknown'}
            )
            
            # Create or update match
            match_date = datetime.fromisoformat(match_data['date'].replace('Z', '+00:00'))
            season = f"{match_date.year}-{match_date.year + 1}"
            
            ChampionsLeagueMatch.objects.update_or_create(
                team_a=team if match_data['home_team'] == team_name else opponent,
                team_b=opponent if match_data['home_team'] == team_name else team,
                match_date=match_date,
                season=season,
                defaults={
                    'team_a_score': match_data['home_score'],
                    'team_b_score': match_data['away_score'],
                    'tournament_stage': match_data.get('stage', 'GROUP'),
                }
            )
        
        return True
    except Exception as e:
        print(f"Sync error: {e}")
        return False


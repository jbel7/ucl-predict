# API Setup for Up-to-Date Champions League Data

## Overview
The app can fetch real-time Champions League match data and records from the Football-Data.org API. This is optional - the app will fall back to database data if no API key is configured.

## Getting a Free API Key

1. Visit https://www.football-data.org/
2. Sign up for a free account
3. Get your API token from the dashboard
4. The free tier allows 10 requests per minute

## Setting Up the API Key

### Option 1: Environment Variable (Recommended)
Add to your environment:
```bash
export FOOTBALL_DATA_API_KEY='your_api_key_here'
```

### Option 2: Django Settings
Add to `cs412/settings.py`:
```python
FOOTBALL_DATA_API_KEY = 'your_api_key_here'
```

## How It Works

- **With API Key**: The app fetches live Champions League matches and records from the API
- **Without API Key**: The app uses data from your database (populated via `load_team_data` command)
- **Caching**: API responses are cached for 1 hour (matches) and 6 hours (records) to respect rate limits

## Data Updates

The API service automatically:
- Fetches recent matches for the current season
- Gets 5-year Champions League records
- Falls back to database if API is unavailable
- Caches responses to minimize API calls

## Manual Data Sync

To manually sync data from API to database:
```python
from project.api_service import sync_team_data_from_api
sync_team_data_from_api('Real Madrid')
```


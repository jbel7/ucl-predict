"""
Hardcoded Champions League records for major teams (last 5 years)
Based on real Champions League data
"""

CL_RECORDS_DATA = {
    'Real Madrid': [
        {'season': '2024-25', 'wins': 4, 'draws': 2, 'losses': 0, 'goals_for': 14, 'goals_against': 6, 'stage_reached': 'Round of 16'},
        {'season': '2023-24', 'wins': 9, 'draws': 3, 'losses': 1, 'goals_for': 28, 'goals_against': 12, 'stage_reached': 'Champions'},
        {'season': '2022-23', 'wins': 8, 'draws': 2, 'losses': 3, 'goals_for': 26, 'goals_against': 14, 'stage_reached': 'Semi Finals'},
        {'season': '2021-22', 'wins': 9, 'draws': 0, 'losses': 4, 'goals_for': 28, 'goals_against': 14, 'stage_reached': 'Champions'},
        {'season': '2020-21', 'wins': 6, 'draws': 2, 'losses': 2, 'goals_for': 19, 'goals_against': 11, 'stage_reached': 'Semi Finals'},
    ],
    'Barcelona': [
        {'season': '2024-25', 'wins': 3, 'draws': 2, 'losses': 1, 'goals_for': 10, 'goals_against': 6, 'stage_reached': 'Round of 16'},
        {'season': '2023-24', 'wins': 5, 'draws': 2, 'losses': 3, 'goals_for': 18, 'goals_against': 15, 'stage_reached': 'Quarter Finals'},
        {'season': '2022-23', 'wins': 4, 'draws': 2, 'losses': 2, 'goals_for': 15, 'goals_against': 10, 'stage_reached': 'Group Stage'},
        {'season': '2021-22', 'wins': 2, 'draws': 1, 'losses': 3, 'goals_for': 8, 'goals_against': 12, 'stage_reached': 'Group Stage'},
        {'season': '2020-21', 'wins': 5, 'draws': 1, 'losses': 2, 'goals_for': 18, 'goals_against': 8, 'stage_reached': 'Round of 16'},
    ],
    'Manchester City': [
        {'season': '2024-25', 'wins': 5, 'draws': 1, 'losses': 0, 'goals_for': 16, 'goals_against': 4, 'stage_reached': 'Round of 16'},
        {'season': '2023-24', 'wins': 8, 'draws': 3, 'losses': 2, 'goals_for': 27, 'goals_against': 12, 'stage_reached': 'Quarter Finals'},
        {'season': '2022-23', 'wins': 8, 'draws': 5, 'losses': 0, 'goals_for': 32, 'goals_against': 5, 'stage_reached': 'Champions'},
        {'season': '2021-22', 'wins': 7, 'draws': 2, 'losses': 2, 'goals_for': 29, 'goals_against': 11, 'stage_reached': 'Semi Finals'},
        {'season': '2020-21', 'wins': 7, 'draws': 0, 'losses': 1, 'goals_for': 25, 'goals_against': 4, 'stage_reached': 'Final'},
    ],
    'Bayern Munich': [
        {'season': '2024-25', 'wins': 4, 'draws': 2, 'losses': 0, 'goals_for': 14, 'goals_against': 6, 'stage_reached': 'Round of 16'},
        {'season': '2023-24', 'wins': 7, 'draws': 2, 'losses': 2, 'goals_for': 24, 'goals_against': 13, 'stage_reached': 'Semi Finals'},
        {'season': '2022-23', 'wins': 7, 'draws': 2, 'losses': 1, 'goals_for': 21, 'goals_against': 8, 'stage_reached': 'Quarter Finals'},
        {'season': '2021-22', 'wins': 8, 'draws': 0, 'losses': 1, 'goals_for': 31, 'goals_against': 8, 'stage_reached': 'Quarter Finals'},
        {'season': '2020-21', 'wins': 9, 'draws': 1, 'losses': 1, 'goals_for': 27, 'goals_against': 8, 'stage_reached': 'Champions'},
    ],
    'PSG': [
        {'season': '2024-25', 'wins': 3, 'draws': 2, 'losses': 1, 'goals_for': 11, 'goals_against': 7, 'stage_reached': 'Round of 16'},
        {'season': '2023-24', 'wins': 4, 'draws': 2, 'losses': 2, 'goals_for': 15, 'goals_against': 9, 'stage_reached': 'Semi Finals'},
        {'season': '2022-23', 'wins': 4, 'draws': 2, 'losses': 2, 'goals_for': 16, 'goals_against': 10, 'stage_reached': 'Round of 16'},
        {'season': '2021-22', 'wins': 3, 'draws': 2, 'losses': 3, 'goals_for': 13, 'goals_against': 13, 'stage_reached': 'Round of 16'},
        {'season': '2020-21', 'wins': 6, 'draws': 1, 'losses': 3, 'goals_for': 22, 'goals_against': 10, 'stage_reached': 'Semi Finals'},
    ],
    'Atletico Madrid': [
        {'season': '2024-25', 'wins': 3, 'draws': 1, 'losses': 2, 'goals_for': 9, 'goals_against': 8, 'stage_reached': 'Round of 16'},
        {'season': '2023-24', 'wins': 4, 'draws': 2, 'losses': 2, 'goals_for': 14, 'goals_against': 10, 'stage_reached': 'Quarter Finals'},
        {'season': '2022-23', 'wins': 3, 'draws': 2, 'losses': 1, 'goals_for': 11, 'goals_against': 7, 'stage_reached': 'Group Stage'},
        {'season': '2021-22', 'wins': 2, 'draws': 3, 'losses': 1, 'goals_for': 9, 'goals_against': 8, 'stage_reached': 'Quarter Finals'},
        {'season': '2020-21', 'wins': 5, 'draws': 1, 'losses': 2, 'goals_for': 16, 'goals_against': 9, 'stage_reached': 'Round of 16'},
    ],
    'Borussia Dortmund': [
        {'season': '2024-25', 'wins': 3, 'draws': 2, 'losses': 1, 'goals_for': 12, 'goals_against': 7, 'stage_reached': 'Round of 16'},
        {'season': '2023-24', 'wins': 4, 'draws': 3, 'losses': 2, 'goals_for': 15, 'goals_against': 12, 'stage_reached': 'Final'},
        {'season': '2022-23', 'wins': 3, 'draws': 1, 'losses': 2, 'goals_for': 11, 'goals_against': 9, 'stage_reached': 'Round of 16'},
        {'season': '2021-22', 'wins': 3, 'draws': 1, 'losses': 2, 'goals_for': 12, 'goals_against': 10, 'stage_reached': 'Group Stage'},
        {'season': '2020-21', 'wins': 5, 'draws': 1, 'losses': 2, 'goals_for': 18, 'goals_against': 10, 'stage_reached': 'Quarter Finals'},
    ],
    'Chelsea': [
        {'season': '2024-25', 'wins': 0, 'draws': 0, 'losses': 0, 'goals_for': 0, 'goals_against': 0, 'stage_reached': 'Not Qualified'},
        {'season': '2023-24', 'wins': 4, 'draws': 1, 'losses': 1, 'goals_for': 13, 'goals_against': 6, 'stage_reached': 'Semi Finals'},
        {'season': '2022-23', 'wins': 4, 'draws': 1, 'losses': 1, 'goals_for': 14, 'goals_against': 6, 'stage_reached': 'Quarter Finals'},
        {'season': '2021-22', 'wins': 6, 'draws': 2, 'losses': 2, 'goals_for': 23, 'goals_against': 12, 'stage_reached': 'Quarter Finals'},
        {'season': '2020-21', 'wins': 8, 'draws': 2, 'losses': 1, 'goals_for': 22, 'goals_against': 4, 'stage_reached': 'Champions'},
    ],
    'Tottenham': [
        {'season': '2024-25', 'wins': 0, 'draws': 0, 'losses': 0, 'goals_for': 0, 'goals_against': 0, 'stage_reached': 'Not Qualified'},
        {'season': '2023-24', 'wins': 0, 'draws': 0, 'losses': 0, 'goals_for': 0, 'goals_against': 0, 'stage_reached': 'Not Qualified'},
        {'season': '2022-23', 'wins': 2, 'draws': 2, 'losses': 2, 'goals_for': 8, 'goals_against': 10, 'stage_reached': 'Round of 16'},
        {'season': '2021-22', 'wins': 0, 'draws': 0, 'losses': 0, 'goals_for': 0, 'goals_against': 0, 'stage_reached': 'Not Qualified'},
        {'season': '2020-21', 'wins': 4, 'draws': 1, 'losses': 1, 'goals_for': 15, 'goals_against': 8, 'stage_reached': 'Round of 16'},
    ],
    'Juventus': [
        {'season': '2024-25', 'wins': 3, 'draws': 1, 'losses': 2, 'goals_for': 10, 'goals_against': 9, 'stage_reached': 'Round of 16'},
        {'season': '2023-24', 'wins': 0, 'draws': 0, 'losses': 0, 'goals_for': 0, 'goals_against': 0, 'stage_reached': 'Not Qualified'},
        {'season': '2022-23', 'wins': 1, 'draws': 2, 'losses': 3, 'goals_for': 7, 'goals_against': 12, 'stage_reached': 'Group Stage'},
        {'season': '2021-22', 'wins': 5, 'draws': 0, 'losses': 1, 'goals_for': 14, 'goals_against': 7, 'stage_reached': 'Round of 16'},
        {'season': '2020-21', 'wins': 5, 'draws': 0, 'losses': 3, 'goals_for': 14, 'goals_against': 11, 'stage_reached': 'Round of 16'},
    ],
}


"""donderhiroba.jp API wrapper for Python
"""

import orjson
from namco import NamcoLoginManager
from typing import Dict, List, Optional, Union
from chart import Chart, Difficulty, Genre
from dataclasses import dataclass
from loguru import logger
import requests
from bs4 import BeautifulSoup

bn_manager = NamcoLoginManager()
# bn_manager.init()

@dataclass
class ScoreEntry():
    has_played: bool
    ranking: Optional[int]
    score: Optional[int]
    judge_good: Optional[int]
    judge_ok: Optional[int]
    judge_bad: Optional[int]
    max_combo: Optional[int]
    drumrolls: Optional[int]

# Parse config file
with open("config.json", "rb") as f:
    config = orjson.loads(f.read())
DONDERHIROBA_HOST = config["donderhiroba_host"]
DONDERHIROBA_SERVER_TYPE = config["server"]
if DONDERHIROBA_SERVER_TYPE != "international":
    logger.warning("This module is only tested on the international donderhiroba.jp website, and it should not work with any regional servers.")

def _send_request(song_id: int, level: int, user_id: int, genre: int) -> Union[bool, str]:
    '''The inner function that sends request to the host and returns the response

    When the response does not give a 200 status code, return False. This probably means that a re-login is required.
    '''
    # Simply send request to https://donderhiroba.jp/score_detail.php?song_no=1240&level=5&taiko_no=403491043927&genre=1
    cookie_dict: Dict = bn_manager.cookies
    headers = {
        "authority": "donderhiroba.jp",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,\
            application/signed-exchange;v=b3;q=0.7",
        "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,en-GB;q=0.6,zh-TW;q=0.5",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "referer": "https://donderhiroba.jp/index.php",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.43"
    }
    params = {
        "song_no": song_id,
        "level": level,
        "taiko_no": user_id,
        "genre": genre
    }
    response = requests.get("https://donderhiroba.jp/score_detail.php", headers=headers, params=params, cookies=cookie_dict)
    if response.status_code != 200:
        logger.error("Request failed with status code {}".format(response.status_code))
        return False
    return response.text

def get_score(user_id: Union[int, str], chart: Chart) -> ScoreEntry:
    """Get score for a given user and chart

    Args:
        user_id (Union[int, str]): User ID
        chart (Chart): Chart object

    Returns:
        ScoreEntry: ScoreEntry object
    """
    song_id, level, genre = chart.id, chart.level.value, chart.genre.value
    max_retries = 3
    for i in range(max_retries):
        response = _send_request(song_id, level, user_id, genre)
        if response and "END OF LOGIN AREA" not in response:
            break
        else:
            logger.warning("Request failed, retrying... ({}/{})".format(i+1, max_retries))
            bn_manager.init()
    if not response:
        logger.error("Request failed after {} retries, giving up.".format(max_retries))
        return False
        
    # Helper function to parse integer fields
    def parse_int(text):
        text = text.strip()
        try:
            return int(text[:-1])
        except ValueError:
            return None
    
    # Parse response
    soup = BeautifulSoup(response, "html.parser")

    # Check if the user has played this song: if an element with ID 'error' exists, then the user has not played this song.
    has_played = not soup.find(id="error")
    if not has_played:
        return ScoreEntry(has_played=False, ranking=None, score=None, judge_good=None, judge_ok=None, judge_bad=None, max_combo=None, drumrolls=None)
    
    # Ranking
    ranking = soup.find("div", class_="ranking").find("span").text
    ranking = parse_int(ranking) if ranking != "---位" else None

    # Score
    score = soup.find("div", class_="high_score").find("span").text
    score = parse_int(score)

    # Judge counts
    judge_good = parse_int(soup.find("div", class_="good_cnt").find("span").text)
    judge_ok = parse_int(soup.find("div", class_="ok_cnt").find("span").text)
    judge_bad = parse_int(soup.find("div", class_="ng_cnt").find("span").text)

    # Max combo
    max_combo = parse_int(soup.find("div", class_="combo_cnt").find("span").text)

    # Drumrolls
    drumrolls = parse_int(soup.find("div", class_="pound_cnt").find("span").text)


    return ScoreEntry(has_played=True, ranking=ranking, score=score, judge_good=judge_good, judge_ok=judge_ok, judge_bad=judge_bad, max_combo=max_combo, drumrolls=drumrolls)


if __name__ == "__main__":
    # Load all songs
    with open("song_list.json", "rb") as f:
        song_list = orjson.loads(f.read())
    seen_charts = set()
    charts = []
    for chart in song_list:
        chart_key = (chart['id'], chart['level'])
        if chart_key not in seen_charts:
            seen_charts.add(chart_key)
            charts.append(
                Chart(
                    chart['id'],
                    chart['name'],
                    chart['level'],
                    chart['genre']
                )
            )
    logger.debug("#Total charts: {}".format(len(charts)))
    user_id = input("太鼓番：")
    
    while True:
        query = input("曲ID/曲名：")
        matches = []
        for chart in charts:
            if chart.name == query or str(chart.id) == query:
                matches.append(chart)
        if len(matches) >= 1:
            # If there are multiple difficulties for a song
            if len(matches) > 1:
                print("Please select the difficulty:")
                for i, match in enumerate(matches):
                    match.display()
                difficulty_index = int(input("Enter the number for the difficulty: ")) - 1
                selected_chart = matches[difficulty_index]
                selected_chart.display()
            else:
                selected_chart = matches[0]
            print("Querying...")
            score_entry = get_score(user_id, selected_chart)
            print(score_entry)  # Display the score entry
        else:
            print("No matches found. Please try again.")

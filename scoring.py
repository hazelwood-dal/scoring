import json
import os
import re
import requests
import time
import urllib3

SCORE_FILE = "score_history.json"

# Load existing score history at startup
if os.path.exists(SCORE_FILE):
    with open(SCORE_FILE, "r") as f:
        score_history = json.load(f)
else:
    score_history = {}


def save_scores():
    with open(SCORE_FILE, "w") as f:
        json.dump(score_history, f)


def accumulate_score(result):
    key = f"{result['team']}::{result['host']}::{result['endpoint']}"
    score_history[key] = score_history.get(key, 0) + result['score']
    result['total_score'] = score_history[key]
    save_scores()
    return result


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TEAM_OCTETS = {
    "Team 1": 1, "Team 2": 2, "Team 3": 3, "Team 4": 4,
    "Team 5": 5, "Team 6": 6, "Team 7": 7
}

CRIT_ENDPOINTS = [
    "/api/pumpSTATUS", "/api/crit1STATUS", "/api/crit2STATUS", "/api/crit3STATUS"
]

NONCRIT_ENDPOINTS = [
    "/api/SewagepumpSTATUS", "/api/Noncrit1STATUS", "/api/Noncrit2STATUS", "/api/Noncrit3STATUS"
]

CRIT_HOSTS = [("https", "25")]
NONCRIT_HOSTS = [("http", "26")]

score_history = {}  # key = team+endpoint+host, value = total score


def check_endpoint(team, protocol, host_suffix, octet, endpoint):
    ip = f"172.16.{octet}.{host_suffix}"
    url = f"{protocol}://{ip}{endpoint}"
    try:
        start = time.time()
        response = requests.get(url, timeout=10, verify=False)
        end = time.time()
        duration_ms = (end - start) * 1000

        match = re.search(r"<p>(.*?)</p>", response.text, re.IGNORECASE)
        status_text = match.group(1).strip() if match else "Unknown"
        print(f"{url} → {status_text}")

        score = 10 if status_text.lower() == "on" else 0

        return {
            "team": team,
            "host": ip,
            "protocol": protocol,
            "endpoint": endpoint,
            "status": status_text,
            "status_code": response.status_code,
            "response_time_ms": round(duration_ms, 2),
            "score": score,
            "error": ""
        }

    except Exception as e:
        return {
            "team": team,
            "host": ip,
            "protocol": protocol,
            "endpoint": endpoint,
            "status": "N/A",
            "status_code": None,
            "response_time_ms": None,
            "score": 0,
            "error": str(e)
        }



def grade_all_teams():
    results = []
    for team, octet in TEAM_OCTETS.items():
        # Check critical endpoints
        for protocol, host_suffix in CRIT_HOSTS:
            for endpoint in CRIT_ENDPOINTS:
                result = check_endpoint(team, protocol, host_suffix, octet, endpoint)
                result = accumulate_score(result)
                results.append(result)
        # Check non-critical endpoints
        for protocol, host_suffix in NONCRIT_HOSTS:
            for endpoint in NONCRIT_ENDPOINTS:
                result = check_endpoint(team, protocol, host_suffix, octet, endpoint)
                result = accumulate_score(result)
                results.append(result)
    return results


def main():
    results = grade_all_teams()
    for r in results:
        print(r)


if __name__ == "__main__":
    main()

import re
import time

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TEAM_OCTETS = {
    "Team 1": 1,
    "Team 2": 2,
    "Team 3": 3,
    "Team 4": 4,
    "Team 5": 5,
    "Team 6": 6,
    "Team 7": 7
}

ENDPOINTS = [
    "/api/pumpSTATUS",
    "/api/crit1STATUS",
    "/api/crit2STATUS",
    "/api/crit3STATUS",
]

HOSTS = [
    ("https", "25"),  # HTTPS
    ("http", "26"),  # HTTP
]


def check_endpoint(team, protocol, host_suffix, octet, endpoint):
    ip = f"172.16.{octet}.{host_suffix}"
    url = f"{protocol}://{ip}{endpoint}"
    try:
        start = time.time()
        #print(url)
        response = requests.get(url, timeout=10, verify=False)
        #print(response.text)
        end = time.time()
        duration_ms = (end - start) * 1000

        # Parse <p>...</p> from HTML
        match = re.search(r"<p>(.*?)</p>", response.text, re.IGNORECASE)
        print(match.group(1).strip())
        status_text = match.group(1).strip() if match else "Unknown"

        # Award points only if status is "On"
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
        # Still return a row even if error
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
        for protocol, host_suffix in HOSTS:
            for endpoint in ENDPOINTS:
                result = check_endpoint(team, protocol, host_suffix, octet, endpoint)
                #print(result)
                results.append(result)
    return results

def main():

    results = grade_all_teams()
    #print(results)


if __name__ == "__main__":
    main()

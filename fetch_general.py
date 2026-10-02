import json
import urllib.request

# url for general index api
url = "https://api.zeroeval.com/leaderboard/indexes/compact?payloadVersion=2&categories=general"

# user agent header to prevent 403
headers = {"user-agent": "mozilla/5.0 (windows nt 10.0; win64; x64)"}

req = urllib.request.Request(url, headers=headers)

try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode("utf-8"))

    # save index data to json file
    output_file = "general_leaderboard.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"successfully fetched general leaderboard and saved to {output_file}")
except Exception as err:
    print(f"an error occurred: {err}")

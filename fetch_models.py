import json
import urllib.request

# url for models api
url = "https://api.zeroeval.com/leaderboard/models"

# user agent header to prevent 403
headers = {"user-agent": "mozilla/5.0 (windows nt 10.0; win64; x64)"}

req = urllib.request.Request(url, headers=headers)

try:
    with urllib.request.urlopen(req) as response:
        models = json.loads(response.read().decode("utf-8"))

    # save models to json file
    output_file = "models.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(models, f, ensure_ascii=False, indent=4)

    print(f"successfully fetched {len(models)} models and saved to {output_file}")
except Exception as err:
    print(f"an error occurred: {err}")

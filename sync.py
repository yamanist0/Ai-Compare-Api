import os
import sys
import json
import base64
import urllib.request
import urllib.error

# get secret token from environment
pat = os.environ.get("GH_PAT") or os.environ.get("gh_pat")

repo = "yamanist0/Ai-Compare-Api"
models_url = "https://api.zeroeval.com/leaderboard/models"
general_url = "https://api.zeroeval.com/leaderboard/indexes/compact?payloadVersion=2&categories=general"

# fetch json from url
def fetch_json(url):
    headers = {"user-agent": "mozilla/5.0 (windows nt 10.0; win64; x64)"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode("utf-8"))

# merge models and benchmark stats
def merge_data(models_list, general_data):
    general_models = general_data.get("general", {}).get("models", [])
    gen_map = {item["model_id"]: item for item in general_models}

    merged = []
    for model in models_list:
        m_id = model.get("model_id")
        entry = dict(model)
        
        benchmark = gen_map.get(m_id)
        if benchmark:
            entry["rank"] = benchmark.get("rank")
            entry["conservative"] = benchmark.get("conservative")
            entry["mu"] = benchmark.get("mu")
            entry["sigma"] = benchmark.get("sigma")
            entry["ci_lower"] = benchmark.get("ci_lower")
            entry["ci_upper"] = benchmark.get("ci_upper")
            entry["games_played"] = benchmark.get("games_played")
            entry["rank_delta_14d"] = benchmark.get("rank_delta_14d")
        else:
            entry["rank"] = None
            entry["conservative"] = None
            entry["mu"] = None
            entry["sigma"] = None
            entry["ci_lower"] = None
            entry["ci_upper"] = None
            entry["games_played"] = None
            entry["rank_delta_14d"] = None

        merged.append(entry)

    # sort by conservative score descending
    leaderboard = [m for m in merged if m["conservative"] is not None]
    leaderboard.sort(key=lambda x: x["conservative"], reverse=True)

    return merged, leaderboard

# save files locally or push to github
def save_file(file_path, content_str, commit_message):
    os.makedirs(os.path.dirname(file_path) if os.path.dirname(file_path) else ".", exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content_str)

    if not pat:
        return

    api_url = f"https://api.github.com/repos/{repo}/contents/{file_path}"
    headers = {
        "authorization": f"Bearer {pat}",
        "accept": "application/vnd.github+json",
        "user-agent": "ai-compare-sync",
        "x-github-api-version": "2022-11-28"
    }

    sha = None
    try:
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req) as res:
            remote_file = json.loads(res.read().decode("utf-8"))
            sha = remote_file.get("sha")
            existing_content = base64.b64decode(remote_file.get("content", "")).decode("utf-8")
            if existing_content.strip() == content_str.strip():
                return
    except urllib.error.HTTPError as e:
        if e.code in (404, 409):
            sha = None
        else:
            print(f"warning on {file_path}: {e}")

    payload = {
        "message": commit_message,
        "content": base64.b64encode(content_str.encode("utf-8")).decode("utf-8")
    }
    if sha:
        payload["sha"] = sha

    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(api_url, data=req_data, headers=headers, method="PUT")
    
    try:
        with urllib.request.urlopen(req):
            print(f"committed {file_path} to {repo}")
    except Exception as err:
        print(f"push error on {file_path}: {err}")

# execute sync job
def main():
    print("fetching models data...")
    models_data = fetch_json(models_url)
    
    print("fetching leaderboard data...")
    general_data = fetch_json(general_url)

    print("merging specs and benchmarks...")
    all_models, leaderboard = merge_data(models_data, general_data)

    all_json_str = json.dumps(all_models, ensure_ascii=False, indent=2)
    leaderboard_json_str = json.dumps(leaderboard, ensure_ascii=False, indent=2)
    models_json_str = json.dumps(models_data, ensure_ascii=False, indent=2)
    general_json_str = json.dumps(general_data, ensure_ascii=False, indent=2)

    save_file("api/all.json", all_json_str, "update api/all.json")
    save_file("api/leaderboard.json", leaderboard_json_str, "update api/leaderboard.json")
    save_file("models.json", models_json_str, "update models.json")
    save_file("general.json", general_json_str, "update general.json")

    # write all individual model files
    for m in all_models:
        mid = m.get("model_id")
        if mid:
            m_str = json.dumps(m, ensure_ascii=False, indent=2)
            model_file = f"api/models/{mid}.json"
            save_file(model_file, m_str, f"update {model_file}")

    print(f"done! synced {len(all_models)} total models and {len(leaderboard)} ranked models")

if __name__ == "__main__":
    main()

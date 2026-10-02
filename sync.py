import os
import sys
import json
import urllib.request
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

# save files locally
def save_file(file_path, content_str, commit_message=None):
    os.makedirs(os.path.dirname(file_path) if os.path.dirname(file_path) else ".", exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content_str)

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

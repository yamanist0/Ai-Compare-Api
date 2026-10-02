import os
import sys
import json
import difflib
import urllib.request
import urllib.error

# helper for fetching data
DEFAULT_REMOTE_URL = "https://yamanist0.github.io/Ai-Compare-Api/data/all.json"
LOCAL_DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "all.json")

class AICompareClient:
    def __init__(self, data_source=None):
        self.models = []
        self.by_id = {}
        self.by_name = {}
        self.all_keys = []
        self.load_data(data_source)

    def load_data(self, data_source=None):
        # load local json if exists or fetch from remote
        if data_source is None:
            if os.path.exists(LOCAL_DATA_PATH):
                with open(LOCAL_DATA_PATH, "r", encoding="utf-8") as f:
                    self.models = json.load(f)
            else:
                req = urllib.request.Request(DEFAULT_REMOTE_URL, headers={"user-agent": "ai-compare-client"})
                with urllib.request.urlopen(req) as res:
                    self.models = json.loads(res.read().decode("utf-8"))
        elif isinstance(data_source, str):
            if data_source.startswith("http"):
                req = urllib.request.Request(data_source, headers={"user-agent": "ai-compare-client"})
                with urllib.request.urlopen(req) as res:
                    self.models = json.loads(res.read().decode("utf-8"))
            else:
                with open(data_source, "r", encoding="utf-8") as f:
                    self.models = json.load(f)
        elif isinstance(data_source, list):
            self.models = data_source

        # build lookup maps
        self.by_id = {}
        self.by_name = {}
        self.all_keys = []

        for m in self.models:
            mid = str(m.get("model_id", "")).strip().lower()
            name = str(m.get("name", "")).strip().lower()
            if mid:
                self.by_id[mid] = m
                if mid not in self.all_keys:
                    self.all_keys.append(mid)
            if name:
                self.by_name[name] = m
                if name not in self.all_keys:
                    self.all_keys.append(name)

    # normalize names to lowercase
    def normalize_name(self, name):
        if not name:
            return ""
        return str(name).strip().lower()

    # find closest model match
    def find_closest(self, query):
        clean_q = self.normalize_name(query)
        if not clean_q:
            return None, []

        # direct match check
        if clean_q in self.by_id:
            return self.by_id[clean_q]["model_id"], [self.by_id[clean_q]["model_id"]]
        if clean_q in self.by_name:
            return self.by_name[clean_q]["model_id"], [self.by_name[clean_q]["model_id"]]

        # substring check
        substring_matches = []
        for key in self.all_keys:
            if clean_q in key or key in clean_q:
                model = self.by_id.get(key) or self.by_name.get(key)
                if model and model["model_id"] not in substring_matches:
                    substring_matches.append(model["model_id"])

        # difflib fuzzy matching
        fuzzy_matches = difflib.get_close_matches(clean_q, self.all_keys, n=5, cutoff=0.3)
        resolved_fuzzy = []
        for k in fuzzy_matches:
            model = self.by_id.get(k) or self.by_name.get(k)
            if model and model["model_id"] not in resolved_fuzzy:
                resolved_fuzzy.append(model["model_id"])

        all_candidates = []
        for item in substring_matches + resolved_fuzzy:
            if item not in all_candidates:
                all_candidates.append(item)

        best_match = all_candidates[0] if all_candidates else None
        return best_match, all_candidates

    # get all known details of a model
    def get_model(self, name, auto_fuzzy=False):
        clean = self.normalize_name(name)
        if clean in self.by_id:
            return {"status": "success", "data": self.by_id[clean]}
        if clean in self.by_name:
            return {"status": "success", "data": self.by_name[clean]}

        # model not found so handle fuzzy suggestions
        best, suggestions = self.find_closest(clean)

        if auto_fuzzy and best:
            matched_model = self.by_id.get(best)
            return {
                "status": "success",
                "auto_matched": True,
                "searched": name,
                "matched_model_id": best,
                "data": matched_model
            }

        return {
            "status": "error",
            "message": f"model '{name}' not found",
            "searched": name,
            "suggestion": best,
            "all_suggestions": suggestions,
            "hint": "enable auto_fuzzy to automatically pick the closest model"
        }

    # compare multiple models sorted by conservative score
    def compare(self, model_names, auto_fuzzy=False):
        if not model_names or len(model_names) < 2:
            return {
                "status": "error",
                "message": "please provide at least 2 models to compare"
            }

        resolved_models = []
        errors = []

        for raw_name in model_names:
            res = self.get_model(raw_name, auto_fuzzy=auto_fuzzy)
            if res["status"] == "success":
                model_data = res["data"]
                # prevent duplicates in compare list
                if not any(m["model_id"] == model_data["model_id"] for m in resolved_models):
                    item = dict(model_data)
                    if res.get("auto_matched"):
                        item["auto_matched_from"] = raw_name
                    resolved_models.append(item)
            else:
                errors.append(res)

        if errors and not auto_fuzzy:
            return {
                "status": "error",
                "message": "some models could not be found",
                "unresolved": errors
            }

        if len(resolved_models) < 2:
            return {
                "status": "error",
                "message": "at least 2 valid models are required after resolution",
                "resolved": resolved_models,
                "errors": errors
            }

        # sort by conservative score descending
        def sort_key(item):
            val = item.get("conservative")
            return val if val is not None else -999999

        resolved_models.sort(key=sort_key, reverse=True)

        winner = resolved_models[0]
        return {
            "status": "success",
            "total_compared": len(resolved_models),
            "winner": {
                "model_id": winner.get("model_id"),
                "name": winner.get("name"),
                "conservative": winner.get("conservative"),
                "rank": winner.get("rank")
            },
            "models": resolved_models
        }

    # query single property of a model
    def get_property(self, name, property_name, auto_fuzzy=False):
        model_res = self.get_model(name, auto_fuzzy=auto_fuzzy)
        if model_res["status"] != "success":
            return model_res

        model = model_res["data"]
        prop_clean = str(property_name).strip().lower().replace("-", "_").replace(" ", "_")

        # search matching property key
        found_key = None
        for key in model.keys():
            if key.lower() == prop_clean:
                found_key = key
                break

        if found_key is None:
            return {
                "status": "error",
                "message": f"property '{property_name}' not found on model '{model.get('name')}'",
                "available_properties": list(model.keys())
            }

        return {
            "status": "success",
            "model_id": model.get("model_id"),
            "model_name": model.get("name"),
            "property": found_key,
            "value": model[found_key]
        }

    # get top leaderboard models
    def get_leaderboard(self, limit=10):
        ranked = [m for m in self.models if m.get("conservative") is not None]
        ranked.sort(key=lambda x: x["conservative"], reverse=True)
        if limit:
            ranked = ranked[:int(limit)]
        return {
            "status": "success",
            "count": len(ranked),
            "leaderboard": ranked
        }

# cli entry point
def cli():
    client = AICompareClient()
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print("usage:")
        print("  python client.py compare <model1> <model2> ... [--fuzzy]")
        print("  python client.py model <model_name> [--fuzzy]")
        print("  python client.py property <model_name> <prop_name> [--fuzzy]")
        print("  python client.py leaderboard [--limit N]")
        return

    cmd = args[0].lower()
    auto_fuzzy = "--fuzzy" in args or "-f" in args
    clean_args = [a for a in args[1:] if a not in ("--fuzzy", "-f")]

    if cmd == "compare":
        res = client.compare(clean_args, auto_fuzzy=auto_fuzzy)
        print(json.dumps(res, indent=2, ensure_ascii=False))
    elif cmd == "model":
        if not clean_args:
            print("please provide model name")
            return
        res = client.get_model(clean_args[0], auto_fuzzy=auto_fuzzy)
        print(json.dumps(res, indent=2, ensure_ascii=False))
    elif cmd == "property":
        if len(clean_args) < 2:
            print("please provide model name and property name")
            return
        res = client.get_property(clean_args[0], clean_args[1], auto_fuzzy=auto_fuzzy)
        print(json.dumps(res, indent=2, ensure_ascii=False))
    elif cmd == "leaderboard":
        limit = 10
        if "--limit" in args:
            idx = args.index("--limit")
            if idx + 1 < len(args):
                limit = int(args[idx + 1])
        res = client.get_leaderboard(limit=limit)
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print(f"unknown command: {cmd}")

if __name__ == "__main__":
    cli()

import os, json, time

DATA_DIR = "data"
LEADERBOARD_FILE = os.path.join(DATA_DIR, "leaderboard.txt")

def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def save_stats_json(stats):
    ensure_data_dir()
    path = os.path.join(DATA_DIR, f"stats_{int(time.time())}.json")
    with open(path, "w") as f:
        json.dump(stats, f, indent=2)
    return path

def append_leaderboard(name, score):
    ensure_data_dir()
    entries = []
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE,"r") as f:
            for line in f:
                try:
                    entries.append(json.loads(line.strip()))
                except:
                    pass
    entries.append({"name": name, "score": score, "ts": int(time.time())})
    entries = sorted(entries, key=lambda x: x["score"], reverse=True)[:10]
    with open(LEADERBOARD_FILE,"w") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")
    return entries

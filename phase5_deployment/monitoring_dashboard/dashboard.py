import json
import time
from pathlib import Path
from collections import defaultdict

LOG_FILE = Path("usage_logs.jsonl")

def log_request(endpoint, status, latency_ms):
    entry = {
        "timestamp": time.time(),
        "endpoint": endpoint,
        "status": status,
        "latency_ms": latency_ms,
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def summarize():
    if not LOG_FILE.exists():
        return {"message": "No logs yet"}
    total = 0
    errors = 0
    latencies = []
    with open(LOG_FILE) as f:
        for line in f:
            entry = json.loads(line)
            total += 1
            if entry["status"] >= 400:
                errors += 1
            latencies.append(entry["latency_ms"])
    return {
        "total_requests": total,
        "error_rate": round(errors / total * 100, 2) if total else 0,
        "avg_latency_ms": round(sum(latencies) / len(latencies), 2) if latencies else 0,
    }

if __name__ == "__main__":
    print("Usage Summary:", summarize())

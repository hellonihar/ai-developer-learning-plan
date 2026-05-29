import csv
import json
from pathlib import Path

def parse_csv(filepath):
    with open(filepath, newline="") as f:
        return list(csv.DictReader(f))

def parse_json(filepath):
    with open(filepath) as f:
        return json.load(f)

def summarize(data):
    if isinstance(data, list):
        return {"count": len(data), "keys": list(data[0].keys()) if data else []}
    return {"keys": list(data.keys())}

if __name__ == "__main__":
    filepath = Path(__file__).parent / "sample_data.csv"
    data = parse_csv(filepath)
    print(summarize(data))

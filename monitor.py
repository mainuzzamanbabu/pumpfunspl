import time, requests
from evaluator import evaluate_token
from utils_io import init_csv, append_row

API = "https://api.pumpfunapi.org/pumpfun/new/tokens"

def run_monitor(poll_interval=5):
    seen = set()
    init_csv()
    while True:
        resp = requests.get(API, timeout=5)
        if not resp.ok:
            time.sleep(poll_interval)
            continue
        data = resp.json()
        mint = data.get("mint")
        if not mint or mint in seen:
            time.sleep(poll_interval)
            continue
        seen.add(mint)
        eval = evaluate_token(data)
        append_row({
            'timestamp': data.get('timestamp'),
            'name': data.get('name'),
            'symbol': data.get('symbol'),
            'mint': mint,
            'metadata_uri': data.get('metadata'),
            'dev_address': data.get('dev'),
            'score': eval['score'],
            'recommend': eval['recommend'],
            'socials_found': eval['socials'],
            'top_holder_pct': eval['top_holder_pct']
        })
        print(f"[{data.get('symbol')}] scored {eval['score']} → {eval['recommend']}")
        time.sleep(poll_interval)

if __name__ == "__main__":
    run_monitor()

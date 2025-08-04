
import requests

def fetch_social_presence(metadata):
    """
    Extract social links from token metadata content.
    If input is a URL, fetch and parse JSON.
    """
    if not metadata:
        return {}
    if isinstance(metadata, str):
        # Fetch JSON if it's a URL
        try:
            resp = requests.get(metadata, timeout=5)
            if resp.ok:
                metadata = resp.json()
            else:
                return {}
        except Exception:
            return {}

    socials = {}
    for key in ['twitter', 'telegram', 'website']:
        url = metadata.get(key)
        if url:
            socials[key] = url
    return socials


def check_social_activity(socials):
    """
    Simple heuristic to score social quality:
    - Twitter: followers count check via public syndication API
    - Telegram & Website: URL reachable check
    Returns score from 0 to 15.
    """
    score = 0

    twitter_url = socials.get('twitter')
    if twitter_url:
        twitter_handle = twitter_url.rstrip('/').split('/')[-1]
        twitter_api_url = f"https://cdn.syndication.twimg.com/widgets/followbutton/info.json?screen_names={twitter_handle}"
        try:
            r = requests.get(twitter_api_url, timeout=5)
            data = r.json()
            if data and isinstance(data, list):
                followers = data[0].get('followers_count', 0)
                if followers > 1000:
                    score += 10
                elif followers > 100:
                    score += 5
        except Exception:
            pass

    telegram_url = socials.get('telegram')
    if telegram_url:
        try:
            r = requests.head(telegram_url, timeout=5)
            if r.status_code == 200:
                score += 3
        except Exception:
            pass

    website_url = socials.get('website')
    if website_url:
        try:
            r = requests.head(website_url, timeout=5)
            if r.status_code == 200:
                score += 2
        except Exception:
            pass

    return score

def evaluate_token(data, SOME_VOLUME_THRESHOLD=1000):
    """
    Evaluate a Pump.fun token to recommend BUY, WATCH or SKIP based on criteria.

    data: dict containing token info including keys:
          - 'metadata': dict (token metadata JSON)
          - 'mint': mint address string
          - 'top_holder_pct': float
          - 'initial_volume': float
    Returns dict with score, recommendation, and details.
    """
    score = 40  # baseline score
    verdict = "SKIP"
    details = {}

    # ① Social links presence and quality
    metadata = data.get('metadata')
    socials = fetch_social_presence(metadata)
    details['socials'] = socials
    social_score = check_social_activity(socials)
    details['social_quality_score'] = social_score

    if socials:
        score += 15 + social_score

    # ② Developer & freeze authority checks - assumed always true on Pump.fun
    details['mint_authority_revoked'] = True
    details['freeze_authority_revoked'] = True
    score += 20

    # ③ Holder concentration: top holder % (to be fetched externally)
    top_pct = data.get('top_holder_pct')
    details['top_holder_pct'] = top_pct
    if top_pct is not None:
        if top_pct < 15:
            score += 15
        elif top_pct > 35:
            score -= 25

    # ④ Liquidity lock - always true on Pump.fun
    details['lp_lock_ok'] = True
    score += 10

    # ⑤ Trading volume momentum
    vol = data.get('initial_volume')
    details['initial_volume'] = vol
    if vol and vol > SOME_VOLUME_THRESHOLD:
        score += 10

    # Clamp score between 0 and 100
    score = max(0, min(100, score))

    # Final recommendation
    if score >= 70 and socials:
        verdict = "BUY"
    elif score >= 50:
        verdict = "WATCH"
    else:
        verdict = "SKIP"

    return {'score': score, 'recommend': verdict, **details}


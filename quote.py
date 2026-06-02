#!/usr/bin/env python3
import json, os, random, subprocess, sys, textwrap, time, urllib.request
from pathlib import Path

TOKEN      = os.getenv('READWISE_TOKEN', '')
CACHE_FILE = Path.home() / '.cache' / 'readwise_quotes.json'
COUNT_TTL  = 86400  # 1 day

RESET  = "\033[0m"
ITALIC = "" if os.environ.get('TMUX') else "\033[3m"
DIM    = "\033[2m"
CYAN   = "\033[36m"

def get(url):
    req = urllib.request.Request(url, headers={'Authorization': f'Token {TOKEN}'})
    with urllib.request.urlopen(req, timeout=5) as r:
        return json.loads(r.read())

def load_cache():
    try:
        return json.loads(CACHE_FILE.read_text())
    except Exception:
        return {'count': 1000, 'count_at': 0, 'queue': []}

def save_cache(cache):
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache))

def fmt(q):
    pad   = "  "
    lines = textwrap.fill(f'"{q["text"].strip().replace(chr(173), "")}"', width=72 - len(pad)).split('\n')
    tag_str = ("  " + "  ".join(f"{CYAN}#{t}{RESET}{DIM}" for t in q.get('tags', []))) if q.get('tags') else ""
    out = ["\n"]
    for line in lines:
        out.append(f"{pad}{ITALIC}{line}{RESET}")
    out.append("")
    in_tmux = bool(os.environ.get('TMUX'))
    link = (f"\033]8;;{q['url']}\033\\↗\033]8;;\033\\" if not in_tmux else "↗") if q.get('url') else ""
    out.append(f"{pad}{DIM}— {q['author']}, {ITALIC}{q['title']}{RESET}{DIM}{tag_str}  {link}{RESET}")
    out.append("")
    return '\n'.join(out)

def fetch_one(cache):
    if time.time() - cache['count_at'] > COUNT_TTL:
        cache['count'] = get('https://readwise.io/api/v2/highlights/?page_size=1')['count']
        cache['count_at'] = time.time()
    for _ in range(3):
        data = get(f'https://readwise.io/api/v2/highlights/?page_size=1&page={random.randint(1, cache["count"])}')
        if data['results']:
            h = data['results'][0]
            b = get(f'https://readwise.io/api/v2/books/{h["book_id"]}/')
            return {'text': h['text'], 'author': b['author'], 'title': b['title'],
                    'tags': [t['name'] for t in h.get('tags', [])],
                    'url': h.get('readwise_url', '')}

def bg_fetch():
    cache = load_cache()
    try:
        q = fetch_one(cache)
        if q:
            cache['queue'].append(q)
            save_cache(cache)
    except Exception:
        pass

def main():
    if '--fetch' in sys.argv:
        bg_fetch()
        return

    if not TOKEN:
        print("⚠ READWISE_TOKEN not set")
        return

    cache = load_cache()

    if cache['queue']:
        q = cache['queue'].pop(0)  # consume front
        save_cache(cache)
        print(fmt(q))
    else:
        # queue empty — fetch live (first run or lagging behind)
        try:
            q = fetch_one(cache)
            save_cache(cache)
            print(fmt(q) if q else "📚 No highlight found")
        except Exception:
            print("❌ Network error — no cached quotes")
            return

    # always pre-fetch next in background
    subprocess.Popen(
        [sys.executable, __file__, '--fetch'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        start_new_session=True,
    )

if __name__ == '__main__':
    main()

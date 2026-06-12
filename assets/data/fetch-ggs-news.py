#!/usr/bin/env python3
"""
Pull the latest Goodgame Empire news + alerts straight from the official
Community Hub (WordPress REST API) and write them into the homepage feeds.

  - GGE news   -> site-feed.json    ."news"          ("Latest from GGS" panel)
  - GGE alerts -> discord-feed.json ."announcements" ("Announcements" panel)

Other game categories (Big Farm, BitLife, E4K-only) are skipped. The manually
curated fields (events plan, changelog, maxyNotes, primeTimes) are preserved.

Run by the refresh-data GitHub Action (and `bash tools/refresh-all.sh` locally).
"""
import json, os, re, sys, html, urllib.request
from datetime import datetime, timezone

HUB   = "https://communityhub.goodgamestudios.com/wp-json/wp/v2/posts"
HERE  = os.path.dirname(os.path.abspath(__file__))
SITE  = os.path.join(HERE, "site-feed.json")
DISC  = os.path.join(HERE, "discord-feed.json")

# WordPress category term IDs (stable). GGE-positive vs hard other-game.
ALERT_EMPIRE = 2935                       # "alertsempire" -> Announcements
GGE_NEWS = {2718, 2710, 2938, 2945}       # Empire, General, FeaturedEmpire, UpdateNotes
# Only hard-exclude genuinely different games. GGE/E4K share event content, so a
# post co-tagged FeaturedE4K is fine as long as it also has a GGE-positive tag.
HARD_OTHER = {2720, 2721}                  # BigFarm, BitLife

NEWS_MAX, ANN_MAX = 8, 6


def fetch_posts(n=30):
    url = f"{HUB}?per_page={n}&_fields=date,title,categories,link,excerpt"
    req = urllib.request.Request(url, headers={"User-Agent": "gge-toolbox-newsfetch/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def clean(s):
    s = re.sub(r"<[^>]+>", "", s or "")          # strip tags
    return html.unescape(s).strip()


def nice_date(iso):                               # "2026-06-12T09:00:00" -> "12 Jun 2026"
    try:
        return datetime.fromisoformat(iso.replace("Z", "")).strftime("%-d %b %Y")
    except Exception:
        return (iso or "")[:10]


def load(path, fallback):
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        return dict(fallback)


def main():
    posts = fetch_posts()
    news, anns = [], []
    for p in posts:
        cats = set(p.get("categories", []))
        title = clean(p["title"]["rendered"])
        link = p.get("link", "")
        date = nice_date(p.get("date", ""))
        if ALERT_EMPIRE in cats:
            body = clean(p.get("excerpt", {}).get("rendered", ""))[:160]
            # excerpt often just repeats the title — drop it if so
            if body.rstrip(" .") == title.rstrip(" .") or title in body[:len(title) + 3]:
                body = ""
            anns.append({"date": date, "title": title, "body": body, "url": link})
        elif (cats & GGE_NEWS) and not (cats & HARD_OTHER):
            news.append({"date": date, "title": title, "url": link})

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    site = load(SITE, {})
    site["news"] = news[:NEWS_MAX]
    site.setdefault("newsUrl", "https://communityhub.goodgamestudios.com/newshube4k/")
    site["newsUpdated"] = stamp
    with open(SITE, "w") as f:
        json.dump(site, f, ensure_ascii=False, indent=2)
        f.write("\n")

    disc = load(DISC, {"announcements": [], "primeTimes": []})
    disc["announcements"] = anns[:ANN_MAX]
    disc["updated"] = stamp
    disc["note"] = ("announcements auto-pulled from the GGE Community Hub "
                    "(alertsempire category) by assets/data/fetch-ggs-news.py; "
                    "primeTimes still manual.")
    with open(DISC, "w") as f:
        json.dump(disc, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"news: {len(site['news'])} items, announcements: {len(disc['announcements'])} items "
          f"(from {len(posts)} hub posts)")


if __name__ == "__main__":
    main()

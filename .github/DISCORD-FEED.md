# Homepage feed → Prime Times & Announcements

The homepage shows two panels — **Prime Times** and **GGE Announcements** — from
[`assets/data/discord-feed.json`](../assets/data/discord-feed.json).

## Announcements — now AUTOMATIC ✅

**Announcements are auto-pulled from the official GGE Community Hub** (the
`alertsempire` category of its WordPress API) by
[`assets/data/fetch-ggs-news.py`](../assets/data/fetch-ggs-news.py), which runs in
the `refresh-data` GitHub Action. No Discord bot is needed — server-issue /
maintenance / compensation posts land in the Announcements panel within a day of
GGS publishing them. The same script refreshes the "Latest from GGS" news panel.
(If an announcement you saw on Discord never appears, GGS only posted it to
Discord/in-game and not to the Community Hub — the hub is the canonical web source.)

## Prime Times — still manual / optional Discord

Prime-time offers are NOT on the hub, so that panel stays hand-edited (or you can
wire a Discord reader bot as below). A Discord *webhook* can only POST *into* a
channel, not read it, so feeding the site needs a small reader bot or no-code
automation.

## The data file

```json
{
  "updated": "2026-06-10",
  "announcements": [
    { "date": "10 Jun", "title": "Server maintenance", "body": "Back online ~14:00 UTC", "url": "" }
  ],
  "primeTimes": [
    { "date": "10 Jun", "title": "Ruby sale", "body": "+50% bonus rubies, 48h", "url": "" }
  ]
}
```

Newest first. Trim expired prime times so the panel stays current. `url` is
optional. The site shows the latest 6 of each.

## Wiring up the reader

You need a bot with **read access** (the *Message Content* intent) to the two
channels. On each new message it updates `discord-feed.json` in this repo. Two
ways to write the file:

### Option A — commit via the GitHub API (keeps it static)
The bot reads a message, then PUTs the updated JSON to the repo:

```
PUT https://api.github.com/repos/chemiestoolkit/gge-toolbox/contents/assets/data/discord-feed.json
Authorization: Bearer <FINE_GRAINED_PAT with Contents: read & write>
Body: { "message": "feed: update", "content": "<base64 of the new JSON>", "sha": "<current file sha>" }
```

GitHub Pages redeploys automatically on commit, so the panel updates within a
minute or two.

### Option B — host the JSON elsewhere
The bot writes the JSON to any static host / gist / small API, and the site
fetches from there instead. Change the fetch URL in
[`assets/js/home-feed.js`](../assets/js/home-feed.js) (`discord-feed.json`).

## Mapping channels

- **GGE Announcements** channel → `announcements[]`
- **GGE Prime Times** channel → `primeTimes[]`

Parse each message into `{ date, title, body }`. Keep it short — the panels are
a glanceable summary, with a link out for detail.

## The webhooks you have (the other direction)

The webhook URLs you provided POST *into* Discord. They're useful in reverse: the
data-refresh Action (or any site event) can POST a notice like "new equipment
added" or "data refreshed" into those channels. That's optional and separate
from the read-path above.

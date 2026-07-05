#!/usr/bin/env python3
"""
Garmin -> ULTRON/JARVIS -synkkaus.

Hakee paivan hyvinvointi- ja treenidatan Garmin Connectista (epavirallinen
rajapinta - kirjautuu omilla Garmin-tunnuksilla, ei vaadi API-avainta) ja
tyontaa tiivistelman Cloudflare Workerin KV-muistiin (/api/garmin).

Ajetaan GitHub Actionsista aamuisin (ks. .github/workflows/garmin-sync.yml).
Tunnukset tulevat ymparistomuuttujina: GARMIN_EMAIL, GARMIN_PASSWORD, JARVIS_PIN.
"""
import datetime
import json
import os
import sys
import urllib.request

from garminconnect import Garmin

WORKER_URL = "https://jarvis.lassi-salminen3.workers.dev"


def pick(d, *keys):
    """Poimi dictista vain halutut avaimet (None jos ei dict)."""
    if not isinstance(d, dict):
        return None
    out = {k: d[k] for k in keys if k in d and d[k] is not None}
    return out or None


def main():
    email = os.environ["GARMIN_EMAIL"]
    password = os.environ["GARMIN_PASSWORD"]
    pin = os.environ["JARVIS_PIN"]
    today = datetime.date.today()
    cdate = today.isoformat()

    g = Garmin(email, password)
    g.login()

    out = {
        "date": cdate,
        "updated": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    }

    def safe(name, fn):
        try:
            out[name] = fn()
        except Exception as e:  # yksittaisen mittarin kaatuminen ei kaada koko synkkia
            print(f"varoitus: {name} epaonnistui: {e}", file=sys.stderr)
            out[name] = None

    def stats():
        return pick(
            g.get_stats(cdate),
            "totalSteps", "restingHeartRate", "totalKilocalories",
            "bodyBatteryMostRecentValue", "averageStressLevel", "sleepingSeconds",
        )

    def sleep():
        d = (g.get_sleep_data(cdate) or {}).get("dailySleepDTO") or {}
        secs = d.get("sleepTimeSeconds")
        score = ((d.get("sleepScores") or {}).get("overall") or {}).get("value")
        return {"hours": round(secs / 3600, 1) if secs else None, "score": score}

    def readiness():
        r = g.get_training_readiness(cdate)
        item = r[0] if isinstance(r, list) and r else r
        return pick(
            item,
            "score", "level", "feedbackShort", "sleepScore",
            "recoveryTime", "hrvFactorPercent", "acuteLoad",
        )

    def body_battery():
        days = g.get_body_battery(cdate) or []
        day = days[0] if isinstance(days, list) and days else {}
        res = pick(day, "charged", "drained") or {}
        levels = []
        for entry in day.get("bodyBatteryValuesArray") or []:
            if not isinstance(entry, (list, tuple)):
                continue
            # rivissa on aikaleima + taso; taso on ainoa luku valilla 0-100
            for v in reversed(entry):
                if isinstance(v, (int, float)) and not isinstance(v, bool) and 0 <= v <= 100:
                    levels.append(v)
                    break
        if levels:
            res.update({"current": levels[-1], "high": max(levels), "low": min(levels)})
        return res or None

    def hrv():
        return pick(
            (g.get_hrv_data(cdate) or {}).get("hrvSummary"),
            "lastNightAvg", "weeklyAvg", "status",
        )

    def dsw():
        """Garminin paivan treeniehdotus (Daily Suggested Workout).
        Endpointti ei ole dokumentoitu - kokeillaan tunnettuja polkuja."""
        api = getattr(g, "connectapi", None) or g.garth.connectapi
        candidates = [
            f"/workout-service/dsw/{cdate}",
            f"/workout-service/schedule?date={cdate}",
            f"/calendar-service/year/{today.year}/month/{today.month - 1}/day/{today.day}/start/1",
        ]
        for path in candidates:
            try:
                d = api(path)
            except Exception:
                continue
            if not d:
                continue
            if isinstance(d, dict) and "calendarItems" in d:
                items = [
                    pick(i, "title", "workoutName", "itemType", "sportTypeKey")
                    for i in d["calendarItems"]
                    if "workout" in str(i.get("itemType", "")).lower()
                ]
                items = [i for i in items if i]
                if items:
                    return items
                continue
            return d
        return None

    safe("stats", stats)
    safe("sleep", sleep)
    safe("trainingReadiness", readiness)
    safe("bodyBattery", body_battery)
    safe("hrv", hrv)
    safe("dsw", dsw)

    payload = json.dumps(out, ensure_ascii=False)
    if len(payload) > 90000:  # DSW-raakavastaus voi olla iso - pudota se tarvittaessa
        out["dsw"] = None
        payload = json.dumps(out, ensure_ascii=False)

    req = urllib.request.Request(
        WORKER_URL + "/api/garmin",
        data=payload.encode("utf-8"),
        method="PUT",
        headers={"Content-Type": "application/json", "X-Jarvis-Pin": pin},
    )
    with urllib.request.urlopen(req) as resp:
        print("KV vastasi:", resp.status, resp.read()[:200].decode())

    print("Synkattu:", {k: ("ok" if out[k] else "-") if k not in ("date", "updated") else out[k] for k in out})


if __name__ == "__main__":
    main()

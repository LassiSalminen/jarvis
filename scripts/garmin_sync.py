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
import time
import urllib.error
import urllib.request

from garminconnect import Garmin

WORKER_URL = "https://jarvis.lassi-salminen3.workers.dev"
# Cloudflare voi blokata Pythonin oletus-User-Agentin (403) - esiinnytaan selaimena
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) JarvisSync/1.0"

PIN = os.environ["JARVIS_PIN"]


def worker_req(path, data=None, method="GET"):
    """Pyynto Workerille. Palauttaa (status, body-teksti) - ei koskaan heita."""
    headers = {"User-Agent": UA, "X-Jarvis-Pin": PIN}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(WORKER_URL + path, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")[:300]
    except Exception as e:
        return 0, str(e)


def pick(d, *keys):
    """Poimi dictista vain halutut avaimet (None jos ei dict)."""
    if not isinstance(d, dict):
        return None
    out = {k: d[k] for k in keys if k in d and d[k] is not None}
    return out or None


def do_login(email, password):
    """Kirjaudu Garminiin. Ensisijaisesti KV:hen talletetulla istunnolla
    (valttaa Garminin pilvi-IP-rate-limitin), muuten tunnuksilla + uudelleenyritykset."""
    status, tok = worker_req("/api/garmintoken")
    if status == 200 and tok and len(tok) > 100:
        try:
            g = Garmin()
            g.login(tok)  # base64-tokenblob edellisesta onnistuneesta ajosta
            print("Kirjauduttu talletetulla istunnolla.")
            return g, False
        except Exception as e:
            print(f"varoitus: talletettu istunto ei kelvannut ({e}), kirjaudutaan uudestaan", file=sys.stderr)

    last = None
    for attempt in range(3):
        if attempt:
            time.sleep(75)  # Garmin rate-limittaa (429) - odota ennen uutta yritysta
        try:
            g = Garmin(email, password)
            g.login()
            print("Kirjauduttu tunnuksilla.")
            return g, True
        except Exception as e:
            last = e
            print(f"varoitus: kirjautuminen epaonnistui (yritys {attempt + 1}/3): {e}", file=sys.stderr)
    raise SystemExit(f"Kirjautuminen Garminiin epaonnistui: {last}")


def main():
    email = os.environ["GARMIN_EMAIL"]
    password = os.environ["GARMIN_PASSWORD"]
    today = datetime.date.today()
    cdate = today.isoformat()

    g, fresh_login = do_login(email, password)
    if fresh_login:
        # Talleta istunto KV:hen -> seuraavat ajot eivat tarvitse kirjautumista
        try:
            status, body = worker_req("/api/garmintoken", g.garth.dumps().encode(), "PUT")
            print("Istunto talletettu KV:hen:", status)
        except Exception as e:
            print(f"varoitus: istunnon talletus epaonnistui: {e}", file=sys.stderr)

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
            "activeKilocalories", "bmrKilocalories", "consumedKilocalories",
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
        Endpointtia ei ole dokumentoitu - kokeillaan tunnettuja polkuja ja
        kirjataan lokiin mita kukin palauttaa, jotta toimiva loytyy."""
        api = getattr(g, "connectapi", None) or g.garth.connectapi
        candidates = [
            f"/workout-service/dsw/{cdate}",
            f"/workout-service/schedule?date={cdate}",
            f"/calendar-service/year/{today.year}/month/{today.month - 1}/day/{today.day}/start/1",
        ]
        result = None
        for path in candidates:
            try:
                d = api(path)
            except Exception as e:
                print(f"dsw-diag: {path} -> virhe: {str(e)[:120]}", file=sys.stderr)
                continue
            summary = json.dumps(d, ensure_ascii=False)[:200] if d else "(tyhja)"
            print(f"dsw-diag: {path} -> {summary}", file=sys.stderr)
            if not d:
                continue
            if isinstance(d, dict) and "calendarItems" in d:
                items = [
                    pick(i, "title", "workoutName", "itemType", "sportTypeKey")
                    for i in d["calendarItems"]
                    if "workout" in str(i.get("itemType", "")).lower()
                ]
                items = [i for i in items if i]
                if items and result is None:
                    result = items
                continue
            if result is None:
                result = d
        return result

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

    status, body = worker_req("/api/garmin", payload.encode("utf-8"), "PUT")
    print("KV vastasi:", status, body[:200])
    if status != 200:
        raise SystemExit(f"Datan lahetys Workerille epaonnistui: HTTP {status} - {body[:300]}")

    print("Synkattu:", {k: ("ok" if out[k] else "-") if k not in ("date", "updated") else out[k] for k in out})


if __name__ == "__main__":
    main()

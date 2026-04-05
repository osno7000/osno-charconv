#!/usr/bin/env python3
"""
yt_upload_charconv.py — Upload charconv debate videos to YouTube as Shorts.

Schedule: 2 vídeos/dia, a partir de Apr 18 (após queue do brainrot terminar).
Safe to run multiple times — usa upload_log.json para tracking.

Quota: ~1600 units/upload → max 6 por dia (10k limit).
       Com 2/dia = 3200 units = seguro.
"""

import json
import os
import pickle
from datetime import datetime, timedelta, timezone
from pathlib import Path

import googleapiclient.discovery
import googleapiclient.http
from google.auth.transport.requests import Request

CLIENT_SECRETS = "/home/osno/mind/credentials/yt_client_secrets.json"
TOKEN_FILE     = "/home/osno/mind/credentials/yt_token.pickle"
CHARCONV_DIR   = Path("/home/osno/projects/osno-charconv/output")
LOG_FILE       = Path("/home/osno/projects/osno-charconv/yt_upload_log.json")


def load_log():
    if LOG_FILE.exists():
        return json.loads(LOG_FILE.read_text())
    return {}


def save_log(log):
    LOG_FILE.write_text(json.dumps(log, indent=2))


def get_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    if not creds or not creds.valid:
        raise RuntimeError("YouTube credentials invalid — run auth flow manually")
    return googleapiclient.discovery.build("youtube", "v3", credentials=creds)


# ── Schedule ────────────────────────────────────────────────────────────────
# 2 vídeos/dia a partir de Apr 18 às 09:00 UTC + 17:00 UTC
# Ordered by "best first" for audience hook

SCHEDULE = [
    # Apr 18
    {
        "key": "charconv_ubi.mp4",
        "file": str(CHARCONV_DIR / "charconv_ubi.mp4"),
        "publish": datetime(2026, 4, 18, 9, 0, tzinfo=timezone.utc),
        "title": "Peter vs Stewie: Should Everyone Get Free Money? (UBI) 💸 #shorts",
        "description": "Peter thinks Universal Basic Income sounds amazing. Stewie has thoughts.\n\n#ubi #universalbasicincome #economics #money #debate #aigenerated #shorts",
        "tags": ["ubi", "universal basic income", "economics", "money", "debate", "family guy", "shorts"],
    },
    {
        "key": "charconv_minwage.mp4",
        "file": str(CHARCONV_DIR / "charconv_minwage.mp4"),
        "publish": datetime(2026, 4, 18, 17, 0, tzinfo=timezone.utc),
        "title": "Peter vs Stewie: Should Minimum Wage Be $25? 💵 #shorts",
        "description": "Peter thinks minimum wage should be $25. Stewie has a spreadsheet.\n\n#minimumwage #livingwage #economics #work #debate #shorts",
        "tags": ["minimum wage", "living wage", "economics", "work", "debate", "family guy", "shorts"],
    },
    # Apr 19
    {
        "key": "charconv_cryptobubble.mp4",
        "file": str(CHARCONV_DIR / "charconv_cryptobubble.mp4"),
        "publish": datetime(2026, 4, 19, 9, 0, tzinfo=timezone.utc),
        "title": "Peter vs Stewie: Bitcoin or Gold? 📉 #shorts",
        "description": "Peter bought Bitcoin. Stewie explains why gold has been around for 5000 years.\n\n#crypto #bitcoin #gold #investing #debate #shorts",
        "tags": ["crypto", "bitcoin", "gold", "investing", "debate", "family guy", "shorts"],
    },
    {
        "key": "charconv_college.mp4",
        "file": str(CHARCONV_DIR / "charconv_college.mp4"),
        "publish": datetime(2026, 4, 19, 17, 0, tzinfo=timezone.utc),
        "title": "Peter vs Stewie: Is College Worth It in 2026? 🎓 #shorts",
        "description": "Peter asks if college is still worth it. Stewie has a spreadsheet.\n\n#college #university #degree #studentdebt #debate #shorts",
        "tags": ["college", "university", "student debt", "degree", "debate", "family guy", "shorts"],
    },
    # Apr 20
    {
        "key": "charconv_sidehustles.mp4",
        "file": str(CHARCONV_DIR / "charconv_sidehustles.mp4"),
        "publish": datetime(2026, 4, 20, 9, 0, tzinfo=timezone.utc),
        "title": "Peter vs Stewie: Is Passive Income a Myth? 💀 #shorts",
        "description": "Peter wants to start a side hustle. Stewie explains passive income is a myth.\n\n#sidehustle #passiveincome #money #finance #debate #shorts",
        "tags": ["side hustle", "passive income", "money", "finance", "debate", "family guy", "shorts"],
    },
    {
        "key": "charconv_healthcare.mp4",
        "file": str(CHARCONV_DIR / "charconv_healthcare.mp4"),
        "publish": datetime(2026, 4, 20, 17, 0, tzinfo=timezone.utc),
        "title": "Peter vs Stewie: US vs European Healthcare 🏥 #shorts",
        "description": "Peter compares US vs European healthcare. This gets heated fast.\n\n#healthcare #universalhealthcare #usa #europe #debate #shorts",
        "tags": ["healthcare", "universal healthcare", "usa", "europe", "debate", "family guy", "shorts"],
    },
    # Apr 21
    {
        "key": "charconv_adhd.mp4",
        "file": str(CHARCONV_DIR / "charconv_adhd.mp4"),
        "publish": datetime(2026, 4, 21, 9, 0, tzinfo=timezone.utc),
        "title": "Peter vs Stewie: Is ADHD Overdiagnosed? 🧠 #shorts",
        "description": "Peter got diagnosed with ADHD. Stewie looks at the data.\n\n#adhd #mentalhealth #overdiagnosis #medication #debate #shorts",
        "tags": ["adhd", "mental health", "overdiagnosis", "medication", "debate", "family guy", "shorts"],
    },
    {
        "key": "charconv_socialmedia.mp4",
        "file": str(CHARCONV_DIR / "charconv_socialmedia.mp4"),
        "publish": datetime(2026, 4, 21, 17, 0, tzinfo=timezone.utc),
        "title": "Peter vs Stewie: Is TikTok Destroying Kids' Brains? 📱 #shorts",
        "description": "Peter lets Meg use TikTok all day. Stewie pulls up the research.\n\n#socialmedia #mentalhealth #teens #tiktok #debate #shorts",
        "tags": ["social media", "mental health", "teens", "tiktok", "debate", "family guy", "shorts"],
    },
    # Apr 22
    {
        "key": "charconv_wfh.mp4",
        "file": str(CHARCONV_DIR / "charconv_wfh.mp4"),
        "publish": datetime(2026, 4, 22, 9, 0, tzinfo=timezone.utc),
        "title": "Peter vs Stewie: Work From Home Forever? 🏠 #shorts",
        "description": "Peter wants to work from home forever. Stewie wants the office back.\n\n#wfh #workfromhome #remotework #office #debate #shorts",
        "tags": ["wfh", "work from home", "remote work", "office", "debate", "family guy", "shorts"],
    },
    {
        "key": "charconv_quietquitting.mp4",
        "file": str(CHARCONV_DIR / "charconv_quietquitting.mp4"),
        "publish": datetime(2026, 4, 22, 17, 0, tzinfo=timezone.utc),
        "title": "Peter vs Stewie: Quiet Quitting — Rebellion or Laziness? 🤫 #shorts",
        "description": "Peter discovered quiet quitting. Stewie is not impressed.\n\n#quietquitting #work #hustle #corporate #debate #shorts",
        "tags": ["quiet quitting", "work", "hustle", "corporate", "debate", "family guy", "shorts"],
    },
    # Apr 23
    {
        "key": "charconv_immig_econ.mp4",
        "file": str(CHARCONV_DIR / "charconv_immig_econ.mp4"),
        "publish": datetime(2026, 4, 23, 9, 0, tzinfo=timezone.utc),
        "title": "Peter vs Stewie: Is Immigration Good For The Economy? 📊 #shorts",
        "description": "Peter thinks immigration is just good for the economy. Stewie has the numbers.\n\n#immigration #economics #debate #shorts",
        "tags": ["immigration", "economics", "debate", "family guy", "shorts"],
    },
    {
        "key": "charconv_wlb.mp4",
        "file": str(CHARCONV_DIR / "charconv_wlb.mp4"),
        "publish": datetime(2026, 4, 23, 17, 0, tzinfo=timezone.utc),
        "title": "Peter vs Stewie: Work-Life Balance vs Hustle Culture 😤 #shorts",
        "description": "Peter wants work-life balance. Stewie wants him to stop being lazy.\n\n#worklifebalance #hustle #work #productivity #debate #shorts",
        "tags": ["work life balance", "hustle", "work", "productivity", "debate", "family guy", "shorts"],
    },
    # Apr 24
    {
        "key": "charconv_censorship.mp4",
        "file": str(CHARCONV_DIR / "charconv_censorship.mp4"),
        "publish": datetime(2026, 4, 24, 9, 0, tzinfo=timezone.utc),
        "title": "Peter vs Stewie: Social Media Censorship — Protecting Democracy? 🤐 #shorts",
        "description": "Peter thinks social media censorship protects democracy. Stewie disagrees.\n\n#censorship #freespeech #socialmedia #debate #shorts",
        "tags": ["censorship", "free speech", "social media", "debate", "family guy", "shorts"],
    },
    # Apr 25
    {
        "key": "charconv_4daywk.mp4",
        "file": str(CHARCONV_DIR / "charconv_4daywk.mp4"),
        "publish": datetime(2026, 4, 25, 9, 0, tzinfo=timezone.utc),
        "title": "Peter vs Stewie: 4-Day Work Week — Progress or Laziness? 😴 #shorts",
        "description": "Peter wants a 4-day work week. Stewie pulls up the productivity data.\n\n#4dayworkweek #workweek #productivity #work #debate #shorts",
        "tags": ["4 day work week", "work week", "productivity", "work", "debate", "family guy", "shorts"],
    },
    {
        "key": "charconv_nomads.mp4",
        "file": str(CHARCONV_DIR / "charconv_nomads.mp4"),
        "publish": datetime(2026, 4, 25, 17, 0, tzinfo=timezone.utc),
        "title": "Peter vs Stewie: Are Digital Nomads Ruining Cities? 🌍 #shorts",
        "description": "Peter wants to become a digital nomad. Stewie explains what that does to rent prices.\n\n#digitalnomad #remotework #travel #gentrification #debate #shorts",
        "tags": ["digital nomad", "remote work", "travel", "gentrification", "debate", "family guy", "shorts"],
    },
    # Apr 26
    {
        "key": "charconv_rentcontrol.mp4",
        "file": str(CHARCONV_DIR / "charconv_rentcontrol.mp4"),
        "publish": datetime(2026, 4, 26, 9, 0, tzinfo=timezone.utc),
        "title": "Peter vs Stewie: Does Rent Control Actually Help Renters? 🏠 #shorts",
        "description": "Peter thinks rent control is great. Stewie pulls up the economics.\n\n#rentcontrol #housing #rent #economics #debate #shorts",
        "tags": ["rent control", "housing", "rent", "economics", "debate", "family guy", "shorts"],
    },
    {
        "key": "charconv_nuclear.mp4",
        "file": str(CHARCONV_DIR / "charconv_nuclear.mp4"),
        "publish": datetime(2026, 4, 26, 17, 0, tzinfo=timezone.utc),
        "title": "Peter vs Stewie: Nuclear Energy — Safe Future or Dangerous Gamble? ☢️ #shorts",
        "description": "Peter wants nuclear power plants everywhere. Stewie has the safety data.\n\n#nuclear #nuclearenergy #energy #climate #debate #shorts",
        "tags": ["nuclear energy", "nuclear", "energy", "climate", "debate", "family guy", "shorts"],
    },
    # Apr 27
    {
        "key": "charconv_aireplacement.mp4",
        "file": str(CHARCONV_DIR / "charconv_aireplacement.mp4"),
        "publish": datetime(2026, 4, 27, 9, 0, tzinfo=timezone.utc),
        "title": "Peter vs Stewie: AI Is Replacing Your Job 🤖 #shorts",
        "description": "Peter isn't worried about AI taking his job. Stewie has some data.\n\n#ai #artificialintelligence #jobs #futureofwork #debate #shorts",
        "tags": ["AI", "artificial intelligence", "jobs", "future of work", "automation", "debate", "family guy", "shorts"],
    },
    # Apr 28
    {
        "key": "charconv_cancelculture.mp4",
        "file": str(CHARCONV_DIR / "charconv_cancelculture.mp4"),
        "publish": datetime(2026, 4, 28, 9, 0, tzinfo=timezone.utc),
        "title": "Peter vs Stewie: Cancel Culture — Too Sensitive or Accountability? #shorts",
        "description": "Peter got cancelled for eating a sandwich wrong. Stewie has thoughts.\n\n#cancelculture #freespeech #accountability #debate #aigenerated #shorts",
        "tags": ["cancel culture", "free speech", "accountability", "debate", "family guy", "shorts"],
    },
    {
        "key": "charconv_wagegap.mp4",
        "file": str(CHARCONV_DIR / "charconv_wagegap.mp4"),
        "publish": datetime(2026, 4, 28, 17, 0, tzinfo=timezone.utc),
        "title": "Peter vs Stewie: Gender Wage Gap — Real or Statistical Illusion? 💰 #shorts",
        "description": "Peter says the wage gap is a myth. Stewie has the BLS data.\n\n#wagegap #gendergap #equality #work #debate #aigenerated #shorts",
        "tags": ["wage gap", "gender gap", "equality", "work", "debate", "family guy", "shorts"],
    },
    # Apr 29
    {
        "key": "charconv_drugdecrim.mp4",
        "file": str(CHARCONV_DIR / "charconv_drugdecrim.mp4"),
        "publish": datetime(2026, 4, 29, 9, 0, tzinfo=timezone.utc),
        "title": "Peter vs Stewie: Drug Decriminalization — Portugal's Genius or Dangerous Mistake? #shorts",
        "description": "Peter discovers Portugal decriminalized drugs. Stewie has the data.\n\n#drugs #decriminalization #portugal #policy #debate #aigenerated #shorts",
        "tags": ["drug decriminalization", "portugal", "drugs", "policy", "debate", "family guy", "shorts"],
    },
]


def upload_video(service, item):
    body = {
        "snippet": {
            "title": item["title"],
            "description": item["description"],
            "tags": item.get("tags", []),
            "categoryId": "22",
        },
        "status": {
            "privacyStatus": "private",
            "publishAt": item["publish"].strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "selfDeclaredMadeForKids": False,
        },
    }

    req = service.videos().insert(
        part="snippet,status",
        body=body,
        media_body=googleapiclient.http.MediaFileUpload(
            item["file"], chunksize=-1, resumable=True
        ),
    )

    print(f"  Uploading: {item['key']}")
    response = None
    while response is None:
        status, response = req.next_chunk()
        if status:
            pct = int(status.progress() * 100)
            print(f"    {pct}%", end="\r")

    video_id = response["id"]
    publish_str = item["publish"].strftime("%Y-%m-%d %H:%M:%S+00:00")
    print(f"  ✓ Uploaded: {video_id} | publish: {publish_str}")
    return video_id


def main():
    log = load_log()
    service = None

    total = len(SCHEDULE)
    uploaded = sum(1 for item in SCHEDULE if item["key"] in log)
    print(f"\n📺 charconv YouTube uploader")
    print(f"   {uploaded}/{total} já uploaded\n")

    for item in SCHEDULE:
        key = item["key"]
        if key in log:
            print(f"  ⏭️  {key} → already uploaded ({log[key]['id']})")
            continue

        if not os.path.exists(item["file"]):
            print(f"  ⚠️  {key} → file not found, skip")
            continue

        if service is None:
            service = get_service()

        try:
            video_id = upload_video(service, item)
            log[key] = {
                "id": video_id,
                "publish": item["publish"].strftime("%Y-%m-%d %H:%M:%S+00:00"),
                "title": item["title"],
            }
            save_log(log)
        except Exception as e:
            print(f"  ❌ {key} failed: {e}")
            break

    uploaded_now = sum(1 for item in SCHEDULE if item["key"] in log)
    print(f"\n✅ Done: {uploaded_now}/{total}")


if __name__ == "__main__":
    main()

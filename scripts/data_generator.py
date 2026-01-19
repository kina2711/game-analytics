import pandas as pd
from faker import Faker
import json, random, uuid, os
import numpy as np
from datetime import datetime, timedelta

fake = Faker()
os.makedirs('data', exist_ok=True)

NUM_USERS = 12000
START_DATE = datetime(2025, 11, 1)
END_DATE = datetime(2025, 11, 30)
COUNTRIES = ['VN', 'TH', 'ID', 'PH', 'MY', 'SG', 'US', 'KR', 'JP', 'TW']
COUNTRY_WEIGHTS = [35, 15, 15, 10, 8, 2, 10, 2, 2, 1]

def generate_final():
    dim_users, dim_levels = [], []
    fact_sessions, fact_gameplay, fact_monetization, fact_health = [], [], [], []
    nested_events_bq = []

    for i in range(1, 11):
        dim_levels.append(
            {"level_id": i, "level_name": f"World 001 - Stage {i}", "difficulty_index": round(0.1 + (i * 0.08), 2)})

    curr_date = START_DATE
    while curr_date <= END_DATE:
        new_users = int(random.randint(200, 500) * np.random.normal(1.0, 0.1))
        for _ in range(new_users):
            u_id, u_country, u_tier = str(uuid.uuid4()), random.choices(COUNTRIES, COUNTRY_WEIGHTS)[0], \
            random.choices(['High-end', 'Mid-range', 'Low-end'], [20, 50, 30])[0]
            u_source = random.choices(['Facebook', 'TikTok', 'Organic'], [35, 45, 20])[0]
            u_camp = f"CAMP_{random.randint(100, 999)}" if u_source != 'Organic' else "None"

            dim_users.append({"user_id": u_id, "install_date": curr_date.date(), "country": u_country,
                              "platform": random.choice(['iOS', 'Android']), "device_tier": u_tier,
                              "media_source": u_source, "campaign_id": u_camp})

            for d in [0, 1, 3, 7]:
                if d > 0 and random.random() > (0.6 / (d + 1)): break
                s_id, start_ts = str(uuid.uuid4()), curr_date + timedelta(days=d, hours=random.randint(0, 22))
                version = random.choice(['1.0.1', '1.0.2', '1.1.0'])

                fact_sessions.append({"session_id": s_id, "user_id": u_id, "start_time": start_ts,
                                      "end_time": start_ts + timedelta(minutes=random.randint(5, 30)),
                                      "app_version": version})

                lvl = random.randint(1, 10)
                is_crash = 1 if (u_tier == 'Low-end' and random.random() > 0.88) else 0
                outcome = random.choices(['level_complete', 'level_fail'], [70, 30])[0]
                reason = random.choice(['Out of time', 'No lives left']) if outcome == 'level_fail' else ""

                fact_gameplay.append(
                    {"event_id": str(uuid.uuid4()), "session_id": s_id, "user_id": u_id, "event_name": outcome,
                     "level_id": lvl, "score": lvl * 100 if outcome == 'level_complete' else 0, "fail_reason": reason})
                fact_health.append({"log_id": str(uuid.uuid4()), "user_id": u_id, "fps_avg": random.randint(20, 60),
                                    "memory_usage_mb": random.randint(200, 900), "is_crash": is_crash})

                r_type, a_fmt, a_usd = 'No_Revenue', 'None', '0'
                if random.random() < 0.3:
                    r_type = random.choices(['IAP', 'Ads'], [40, 60])[0]
                    a_fmt = random.choice(['Rewarded', 'Interstitial', 'Banner']) if r_type == 'Ads' else 'None'
                    a_usd = str(random.choice([0.99, 4.99, 14.99]) if r_type == 'IAP' else 0.05)
                    fact_monetization.append(
                        {"transaction_id": str(uuid.uuid4()), "user_id": u_id, "timestamp": start_ts,
                         "rev_type": r_type, "ad_format": a_fmt, "amount_usd": float(a_usd)})

                nested_events_bq.append({
                    "user_id": u_id, "session_id": s_id, "timestamp": start_ts.isoformat(), "event_name": outcome,
                    "app_version": version,
                    "event_params": [
                        {"key": "country", "value": u_country}, {"key": "device_tier", "value": u_tier},
                        {"key": "media_source", "value": u_source}, {"key": "campaign_id", "value": u_camp},
                        {"key": "level_id", "value": str(lvl)},
                        {"key": "difficulty_index", "value": str(round(0.1 + (lvl * 0.08), 2))},
                        {"key": "is_crash", "value": str(is_crash)}, {"key": "rev_type", "value": r_type},
                        {"key": "ad_format", "value": a_fmt}, {"key": "amount_usd", "value": a_usd},
                        {"key": "fail_reason", "value": reason}
                    ]
                })
        curr_date += timedelta(days=1)

    # Save file
    pd.DataFrame(dim_users).to_csv('data/dim_users.csv', index=False)
    pd.DataFrame(dim_levels).to_csv('data/dim_levels.csv', index=False)
    pd.DataFrame(fact_sessions).to_csv('data/fact_sessions.csv', index=False)
    pd.DataFrame(fact_gameplay).to_csv('data/fact_gameplay_events.csv', index=False)
    pd.DataFrame(fact_monetization).to_csv('data/fact_monetization.csv', index=False)
    pd.DataFrame(fact_health).to_csv('data/fact_technical_health.csv', index=False)
    with open('data/events_nested.json', 'w') as f:
        for e in nested_events_bq: f.write(json.dumps(e) + '\n')
    print("Done")

generate_final()
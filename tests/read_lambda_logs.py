
import boto3
from datetime import datetime, timedelta, timezone

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from config import AWS_PROFILE, AWS_REGION

LOG_GROUP = "/aws/lambda/cloud-document-analyzer-processor"

session = boto3.Session(
    profile_name=AWS_PROFILE,
    region_name=AWS_REGION
)

logs = session.client("logs")

start_time = int(
    (datetime.now(timezone.utc) - timedelta(hours=1)).timestamp() * 1000
)

response = logs.filter_log_events(
    logGroupName=LOG_GROUP,
    startTime=start_time
)

events = response.get("events", [])

if not events:
    print("No Lambda logs found in the last 1 hour.")
else:
    for event in events:
        timestamp = datetime.fromtimestamp(
            event["timestamp"] / 1000,
            tz=timezone.utc
        )

        print(f"[{timestamp.isoformat()}] {event['message']}")

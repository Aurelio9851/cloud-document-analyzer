import boto3
import time

from config import AWS_PROFILE, AWS_REGION

LOG_GROUP = "/aws/lambda/cloud-document-analyzer-processor"


def main():
    session = boto3.Session(
        profile_name=AWS_PROFILE,
        region_name=AWS_REGION
    )

    logs = session.client("logs")

    end_time = int(time.time() * 1000)
    start_time = end_time - (5 * 60 * 1000)

    response = logs.filter_log_events(
        logGroupName=LOG_GROUP,
        startTime=start_time,
        endTime=end_time,
        limit=50
    )

    events = response.get("events", [])

    print(f"Events found: {len(events)}\n")

    for event in events:
        timestamp = time.strftime(
            "%H:%M:%S",
            time.localtime(event["timestamp"] / 1000)
        )

        print(f"[{timestamp}] {event['message'].strip()}")


if __name__ == "__main__":
    main()
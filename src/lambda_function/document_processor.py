
def process_document(
    textract_client,
    bucket,
    object_key,
    notification_topic_arn,
    notification_role_arn
):
    response = textract_client.start_document_analysis(
        DocumentLocation={
            "S3Object": {
                "Bucket": bucket,
                "Name": object_key
            }
        },
        FeatureTypes=["TABLES", "FORMS"],
        NotificationChannel={
            "SNSTopicArn": notification_topic_arn,
            "RoleArn": notification_role_arn
        },
        JobTag=object_key.replace("/", "_")
    )

    result = {
        "bucket": bucket,
        "object_key": object_key,
        "job_id": response["JobId"],
        "status": "STARTED"
    }

    return result

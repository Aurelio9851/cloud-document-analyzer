def process_document(s3_client, bucket, object_key):

    response = s3_client.get_object(
        Bucket=bucket,
        Key=object_key
    )

    content = response["Body"].read().decode("utf-8")

    result = {
        "bucket": bucket,
        "object_key": object_key,
        "content_length": len(content),
        "preview": content[:200]
    }

    return result
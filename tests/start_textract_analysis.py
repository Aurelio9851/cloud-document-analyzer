
import boto3

PROFILE = "cda-dev"
REGION = "eu-west-1"

BUCKET_NAME = "cloud-document-analyzer-562912537127-77ebe154"
DOCUMENT_KEY = "samples/sample-document.pdf"

session = boto3.Session(
    profile_name=PROFILE,
    region_name=REGION
)

textract = session.client("textract")

response = textract.start_document_analysis(
    DocumentLocation={
        "S3Object": {
            "Bucket": BUCKET_NAME,
            "Name": DOCUMENT_KEY
        }
    },
    FeatureTypes=[
        "TABLES",
        "FORMS"
    ]
)

job_id = response["JobId"]

print("Textract analysis started successfully.")
print("Job ID:", job_id)

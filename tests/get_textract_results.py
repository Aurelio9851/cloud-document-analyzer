
import boto3
import time

PROFILE = "cda-dev"
REGION = "eu-west-1"

JOB_ID = (
    "e480406aaefd8c88874f4ef18939852aee7900fdaeda8a9cd26beb2f1f66c8e4"
)

session = boto3.Session(
    profile_name=PROFILE,
    region_name=REGION
)

textract = session.client("textract")

print("Waiting for Textract analysis...")

# Polling: controlliamo ogni 5 secondi
while True:
    response = textract.get_document_analysis(
        JobId=JOB_ID,
        MaxResults=1000
    )

    status = response["JobStatus"]
    print("Job status:", status)

    if status in ("SUCCEEDED", "FAILED", "PARTIAL_SUCCESS"):
        break

    time.sleep(5)

if status == "FAILED":
    raise RuntimeError(
        f"Textract analysis failed: {response.get('StatusMessage')}"
    )

# Recuperiamo tutti i risultati, gestendo la paginazione
blocks = response.get("Blocks", [])

while response.get("NextToken"):
    response = textract.get_document_analysis(
        JobId=JOB_ID,
        MaxResults=1000,
        NextToken=response["NextToken"]
    )
    blocks.extend(response.get("Blocks", []))

# Conteggio dei diversi tipi di blocco
block_counts = {}

for block in blocks:
    block_type = block["BlockType"]
    block_counts[block_type] = block_counts.get(block_type, 0) + 1

print("\nAnalysis completed.")
print("Total blocks:", len(blocks))
print("Block types:", block_counts)

# Estraiamo il testo riconosciuto
print("\n--- EXTRACTED TEXT ---\n")

for block in blocks:
    if block["BlockType"] == "LINE":
        print(block["Text"])

if status == "PARTIAL_SUCCESS":
    print("\nWarning: some pages or elements may not have been processed.")

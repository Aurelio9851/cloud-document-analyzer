
import boto3
from collections import Counter

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

response = textract.get_document_analysis(
    JobId=JOB_ID,
    MaxResults=1000
)

blocks = response.get("Blocks", [])

# Conteggio dei tipi di blocco
counts = Counter(
    block["BlockType"] for block in blocks
)

print("BLOCK TYPES")
for block_type, count in counts.items():
    print(f"{block_type}: {count}")

print("\nSAMPLE BLOCKS")

for block in blocks:
    if block["BlockType"] in (
        "PAGE",
        "LINE",
        "WORD"
    ):
        print({
            "BlockType": block["BlockType"],
            "Id": block.get("Id"),
            "Text": block.get("Text"),
            "Relationships": block.get("Relationships")
        })

        if block["BlockType"] == "WORD":
            break

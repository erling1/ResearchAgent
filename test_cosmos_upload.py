

# cosmos_test_upload.py
import os
import uuid
import datetime
from azure.cosmos import CosmosClient,PartitionKey

# --- Config ---
COSMOS_URI = os.getenv("COSMOS_URI")
COSMOS_KEY = os.getenv("COSMOS_KEY")
DATABASE_NAME = "database1"
CONTAINER_NAME = "container1"

def main():
    # Init Cosmos client
    client = CosmosClient(COSMOS_URI, credential=COSMOS_KEY)

    # Get DB + container
    database = client.get_database_client(DATABASE_NAME)
    container = database.get_container_client(CONTAINER_NAME)

    # Create test document
    unique_id = str(uuid.uuid4())
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d')


    document = {
    "id": unique_id,
    "AIResponse": "all_responses",  # <-- fixed value matching your container PK
    "response_text": "This is a test response for Cosmos upload verification.",
    "metadata": {
        "prompt": "TEST_PROMPT_ONLY",
        "timestamp": timestamp,
        "model": "test-model",
        "source": "cosmos_test_upload.py"
    }
}

    # Upload doc
    result = container.create_item(body=document)
    print("✅ Document uploaded successfully!")
    #print(result)


    query = "SELECT * FROM c WHERE c.AIResponse = @pk"
    parameters = [{"name": "@pk", "value": "AIResponse"}]

    print(f"parameters: {parameters}")

    
    items = list(container.query_items(
        query="SELECT * FROM c",  # no WHERE clause
        enable_cross_partition_query=True  # must enable this to scan all partitions
    ))

    for item in items:
        print(item)

    print(len(items))
    print(type(items))


if __name__ == "__main__":
    main()

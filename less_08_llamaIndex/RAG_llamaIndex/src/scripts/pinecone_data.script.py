import os
import netfree_patch
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = os.getenv("PINECONE_INDEX_NAME")
index = pc.Index(index_name)

stats = index.describe_index_stats()
print(f"Total vector count: {stats['total_vector_count']}")

results = index.list(limit=10)
ids = [res for res in results]

if ids:
    print(f"Found IDs: {ids}")

    fetch_response = index.fetch(ids=[ids[0]])
    print("\n--- Sample Vector Data ---")
    print(fetch_response)
else:
    print("The index is empty.")
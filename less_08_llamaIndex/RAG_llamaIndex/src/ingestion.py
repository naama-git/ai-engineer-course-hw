
import asyncio
import netfree_patch
  
from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
)
from llama_index.core.node_parser import SentenceSplitter
from dotenv import load_dotenv

from config import init_app_settings

load_dotenv()

vector_store, storage_context, pinecone_index = init_app_settings()
index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

def load_data(data_path="./data"):
    try:

        documents = SimpleDirectoryReader(data_path, required_exts=[".md"]).load_data()
        print("Documents loaded")
        return documents
    except Exception as e:
        print(f"Error loading data: {e}")
        return []


def chunk_documents(documents, chunk_size=200, chunk_overlap=20):
    try:
        node_parser = SentenceSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

        nodes = node_parser.get_nodes_from_documents(
            documents
        )
        return nodes
    except Exception as e:
        print(f"Error chunking documents: {e}")
        return []

def embedding_indexing(nodes=None):
    if nodes is None or len(nodes) == 0:
        print("Warning: The list of nodes is empty!")
        return None
    try:
        print(f"Sends {len(nodes)} nodes to Pinecone...")
        index = VectorStoreIndex(
                nodes, 
                storage_context=storage_context,
                show_progress=True 
            )
        return index
    except Exception as e:
        print(f"!!! Critical error in creating the index: {e}")
        return None 

async def ingestion_pipeline():
    stats = pinecone_index.describe_index_stats()
    vector_count = stats['total_vector_count']

    if vector_count > 0:
        print(f"Index already contains {vector_count} vectors. Skipping ingestion.")
        index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
    else:
        print("Index is empty. Starting ingestion process...")
        docs = load_data()
        nodes = chunk_documents(docs)
        index = embedding_indexing(nodes)

    if index is None:                          
        print("Failed to create the index, exiting.")
        return
    return index
    


async def main():
    docs = load_data()
    nodes = chunk_documents(docs)
    index =  embedding_indexing(nodes)
    if index is None:                          
        print("Failed to create the index, exiting.")
        return
    query_engine = index.as_query_engine()
    response = await query_engine.aquery("על מה מדברים המסמכים שלי?")
    print("RESPONSE:",response)

if __name__ == "__main__":
   asyncio.run(main())

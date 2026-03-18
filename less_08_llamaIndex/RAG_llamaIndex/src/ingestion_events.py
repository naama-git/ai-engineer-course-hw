# ------- Event-driven workflow to initialize pinecone index with vector data
# ------- it loads all data files, chancks them and embeds it
# ------- finally, it saves the data into pinecone vector index


import asyncio
import os

from llama_index.core.workflow import Workflow, StartEvent ,StopEvent , Event, step , Context
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

class InitData(Event):
    data_path:str

class ChanckDocuments(Event):
    documents: list
    chunk_size: int = 200
    chunk_overlap: int = 20

class EmbeddingIndexing(Event):
    nodes: list

class IngestionWorkflow(Workflow):
    @step 
    async def InitializeContext(self, ev:StartEvent, ctx:Context)->InitData:
        stats = pinecone_index.describe_index_stats()
        vector_count = stats['total_vector_count']

        if vector_count > 0:
            print(f"Index already contains {vector_count} vectors. Skipping ingestion.")
            return StopEvent(result=index)
      
        await ctx.store.set("index", index)
        return InitData(data_path=ev.data_path)


    @step
    async def load_data(self, ev:InitData, ctx:Context)-> ChanckDocuments| StopEvent:
        # current_index = await ctx.store.get("index")
        try:
            reader = SimpleDirectoryReader(
                ev.data_path, 
                required_exts=[".md", ".MD"], 
                recursive=True, 
                exclude_hidden=False,
                file_metadata=lambda fp: {
                    "directory_name": os.path.basename(os.path.dirname(fp)),
                    "tool": os.path.basename(os.path.dirname(fp)),
                    "file_name": os.path.basename(fp)
                }
            )
            documents = reader.load_data()
            return ChanckDocuments(documents=documents)

        except Exception as e:
            print(f"[load_data] Error: {e}")
            return StopEvent(result=f"Error: {str(e)}")
    
    @step
    async def chunk_documents(self, ev:ChanckDocuments)->EmbeddingIndexing:
        try:
            node_parser = SentenceSplitter(chunk_size=ev.chunk_size, chunk_overlap=ev.chunk_overlap)

            nodes = node_parser.get_nodes_from_documents(
                ev.documents
            )
            return EmbeddingIndexing(nodes=nodes)
        except Exception as e:
            print(f"Error chunking documents: {e}")
            return StopEvent(result=None)
        
    @step
    async def embedding_indexing(self, ev:EmbeddingIndexing)->StopEvent:
        if ev.nodes is None or len(ev.nodes) == 0:
            print("Warning: The list of nodes is empty!")
            return StopEvent(result=None)
        try:
            print(f"Sends {len(ev.nodes)} nodes to Pinecone...")
            index = VectorStoreIndex(
                    ev.nodes, 
                    storage_context=storage_context,
                    show_progress=True 
                )
            return StopEvent(result=index)
        except Exception as e:
            print(f"!!! Critical error in creating the index: {e}")
            return StopEvent(result=None)




if __name__ == "__main__":
    async def main():
        wf = IngestionWorkflow(timeout=120)
        index = await wf.run(data_path="./../data")
        print("Done:", index)

    asyncio.run(main())

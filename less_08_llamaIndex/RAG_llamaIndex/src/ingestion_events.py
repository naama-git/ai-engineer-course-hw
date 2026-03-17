import asyncio
import os

from llama_index.core.workflow import Workflow, StartEvent ,StopEvent , Event, step 
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

class CheckIndex(Event):
    data_path: str
    skip: bool

class ChanckDocuments(Event):
    documents: list
    chunk_size: int = 200
    chunk_overlap: int = 20

class EmbeddingIndexing(Event):
    nodes: list

class IngestionWorkflow(Workflow):

    @step
    async def check_index(self, ev: StartEvent) -> CheckIndex:
        stats = pinecone_index.describe_index_stats()
        already_indexed = stats["total_vector_count"] > 0
        if already_indexed:
            print(f"Index already has {stats['total_vector_count']} vectors, skipping ingestion.")
            # return CheckIndex(data_path=ev.data_path, skip=already_indexed)
        return CheckIndex(data_path=ev.data_path, skip=already_indexed)

    @step
    async def load_data(self, ev:CheckIndex)-> ChanckDocuments|StopEvent:
       
        try:
            reader = SimpleDirectoryReader(
                ev.data_path, 
                required_exts=[".md"], 
                recursive=True, 
                file_metadata=lambda fp: {
                    "directory_name": os.path.basename(os.path.dirname(fp)),
                    "tool": os.path.basename(os.path.dirname(fp)),
                    "file_name": os.path.basename(fp)
                }
            )

            input_files = reader.list_resources()
            files_to_process = []

            for file_path in input_files:
                str_path = str(file_path)
                
                if str_path not in self.index.ref_doc_info:
                    files_to_process.append(file_path)
                else:
                    current_doc = reader.load_file(file_path)
                    if self.index.ref_doc_info[str_path].hash != current_doc[0].hash:
                        files_to_process.append(file_path)

            if not files_to_process:
                print("new files or changes were not found. stops workflow.")
                return StopEvent(result="No changes detected, index is up to date.")

            reader.input_files = files_to_process
            documents = reader.load_data()
            
            print(f"{len(documents)} updates found.")
            return ChanckDocuments(documents=documents)

        except Exception as e:
            print(f"Error during data loading: {e}")
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

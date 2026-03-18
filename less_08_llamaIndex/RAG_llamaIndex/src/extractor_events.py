
# ----- A workflow for data extraction. 
# ----- it loads data, sends it to LLM in order to get it in structured JSON format and save the data in mongoDB
# ----- it uses RootSchema which defines in schemas.py file

import asyncio
from datetime import datetime 
import json
import os
from motor.motor_asyncio import AsyncIOMotorClient
import netfree_patch
from llama_index.core.workflow import Workflow, StartEvent ,StopEvent , Event, step

from llama_index.core import (
    SimpleDirectoryReader
)
from llama_index.llms.google_genai import GoogleGenAI
from schemas import RootSchema
from dotenv import load_dotenv
load_dotenv()


class GetDocs(Event):
    documents:list


class FilteredDocs(Event):
    documents: list

class ExtractedData(Event):
    data:dict

class ExtractorWorkflow(Workflow):

    def __init__(self, collection, mongo_db, llm, **kwargs):
        super().__init__(**kwargs)
        self.collection = collection
        self.mongo_db=mongo_db
        self.llm = llm
        
        
    @step
    async def load_data(self, ev:StartEvent)-> GetDocs| StopEvent:
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
            return GetDocs(documents=documents)

        except Exception as e:
            print(f"[load_data] Error: {e}")
            return StopEvent(result=f"Error: {str(e)}")


    @step
    async def check_existing(self, ev: GetDocs) -> FilteredDocs | StopEvent:
        try:
            # client = AsyncIOMotorClient(os.environ.get("MONGO_URI"))
            # collection = self.collection

            count = await self.collection.count_documents({})
            if count > 0:
                print(f"There are {count} files in DB")
                existing=await self.collection.find_one()
                obj_id = existing["_id"]
                string_id = str(obj_id)
                return StopEvent(result=string_id)
            
            
            # new_docs = []
            # for doc in ev.documents:
            #     file_name = doc.metadata.get("file_name")
            #     exists = await collection.find_one({"file_name": file_name})
                
            #     if not exists:
            #         new_docs.append(doc)
            #     else:
            #         print(f"⏭️ {file_name} already exists in DB. skipping...")

            # if not new_docs:
            #     return StopEvent(result="All files have been processed previously.")
            
            return FilteredDocs(documents=ev.documents)
        except Exception as e:
            return StopEvent(result=f"Database Check Error: {e}")


    @step 
    async def structured_llm(self, ev:FilteredDocs)->ExtractedData|StopEvent:
  
        try:
        #    llm=GoogleGenAI(model=os.environ.get("LLM"), api_key=os.environ.get("GEMINI_API_KEY"))
           sllm= self.llm.as_structured_llm(RootSchema)

           combined_text = "\n\n".join([d.get_content() for d in ev.documents])
           response = await sllm.acomplete(combined_text)
           json_response = json.loads(response.text)
           return ExtractedData(data=json_response)

        except Exception as e:
            print(f"Extraction Failed: {e}")
            return StopEvent(result=None)
        
    @step
    async def save_data(self, ev: ExtractedData) -> StopEvent:
        try:
           
            client = AsyncIOMotorClient(os.environ.get("MONGO_URI"))
            db = client[self.mongo_db]
            collection = db[self.collection]

            data_to_save = ev.data
            data_to_save["processed_at"] = datetime.now()
            
            result = await collection.insert_one(data_to_save)
            
            return StopEvent(result=f"{result.inserted_id}")
        except Exception as e:
            return StopEvent(result=f"Error: {e}")
        

async def main():
    extractor = ExtractorWorkflow(timeout=120)
    res = await extractor.run(data_path="./data")

    print(res)

if __name__ == "__main__":
    asyncio.run(main())
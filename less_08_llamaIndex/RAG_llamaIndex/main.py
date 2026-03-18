import sys
import os
import asyncio

from motor.motor_asyncio import AsyncIOMotorClient

src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')

if src_path not in sys.path:
    sys.path.insert(0, src_path)

from llama_index.llms.google_genai import GoogleGenAI
from llama_index.core.schema import QueryBundle
from llama_index.core.tools import QueryEngineTool
from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.selectors import LLMSingleSelector
from src.mongo_query_events import MongoQueryWorkflow
from dotenv import load_dotenv

from src.config import init_app_settings
from src.mongo_workflow_engine import MongoWorkflowEngine
from src.ingestion_events import IngestionWorkflow
from src.agent_events import AgentWorkFlow
from src.extractor_events import ExtractorWorkflow
from src.chat_ui import build_gradio_app

load_dotenv()
os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"

vector_store, storage_context, pinecone_index = init_app_settings()

pinecone_query_engine = None
mongo_query_engine=None

index=None
router_engine=None

def build_router_engine():

    pinecone_tool = QueryEngineTool.from_defaults(
    query_engine=pinecone_query_engine,
    description="Useful for semantic search of free text, articles, and raw Markdown documents.")

    mongo_tool = QueryEngineTool.from_defaults(
        query_engine=mongo_query_engine, 
        description="Useful for extracting structured data, tables, specific decisions, and statistics from the database."
    )

    global router_engine
    router_engine = RouterQueryEngine(
        selector=LLMSingleSelector.from_defaults(),
        query_engine_tools=[pinecone_tool, mongo_tool],

    )
    

async def initialize_system():
    global pinecone_query_engine, index, mongo_query_engine

    # run ingestion
    ingestion = IngestionWorkflow(timeout=120)
    index = await ingestion.run(data_path="./data")

    if index is None:
        raise RuntimeError("Ingestion failed.")

    # build pinecone query engine via workflow
    qe_workflow = AgentWorkFlow(timeout=30)
    pinecone_query_engine = await qe_workflow.run(index=index, top_k=7)

    if(pinecone_query_engine is None):
        raise RuntimeError("Pinecone query engine is None")

    # build mongo query engine via workflow
    llm=GoogleGenAI(model=os.environ.get("LLM"), api_key=os.environ.get("GEMINI_API_KEY"))
    db_name=os.environ.get("DB_NAME")
    collection_name=os.environ.get("COLLECTION_NAME")
    client = AsyncIOMotorClient(os.environ.get("MONGO_URI"))
    db = client[db_name] 
    collection = db[collection_name]

    # data extraction
    extractor=ExtractorWorkflow(timeout=120, llm=llm, mongo_collection=collection )
    schemaId=await extractor.run(data_path="./data")

    # build query enine
    mongo_wf = MongoQueryWorkflow(mongo_collection=collection, llm=llm)
    mongo_query_engine = MongoWorkflowEngine(workflow=mongo_wf, schema_id=schemaId)
   
    if(mongo_query_engine is None):
        raise RuntimeError("mongo engine is None")
    
    # build router engine
    build_router_engine() 

    if(router_engine is None):
        raise RuntimeError("router engine is None")
    
    print("System and Router ready.")



async def chat_interface(question: str):
    if not question.strip():
        return "Please enter a question.", ""

    bundle = QueryBundle(query_str=question)
    response = await router_engine.aquery(bundle)

    selected_tool = "Unknown"
    tools=["pinecone query engine", "mongo query engne"]
    if "selector_result" in response.metadata:
        selections = response.metadata["selector_result"]
        
    
        if selections:
            actual_list = selections.selections
            first_selection = actual_list[0]
            tool_index = first_selection.index
            selected_tool=tools[tool_index]
            reason = first_selection.reason
            
            print(f"🛠️ Selected tool: {selected_tool}")
            print(f"🤔 Reason: {reason}")
           

    sources_text = "### Sources\n"
    if hasattr(response, "source_nodes"):
        for i, node in enumerate(response.source_nodes, 1):
            fname = node.node.metadata.get("file_name", "Unknown")
            sources_text += f"**{i}. {fname}** (Score: {node.score:.2f})\n"
            
    return str(response), sources_text


async def start_everything():
   
    await initialize_system()
    
    app = build_gradio_app(run_query_fn=chat_interface)
    
    app.launch(server_name="0.0.0.0", server_port=7860, prevent_thread_lock=True)

    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(start_everything())
    except KeyboardInterrupt:
        print("System stopped by user.")

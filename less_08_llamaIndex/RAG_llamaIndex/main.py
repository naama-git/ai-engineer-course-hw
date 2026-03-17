import sys
import os
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')

if src_path not in sys.path:
    sys.path.insert(0, src_path)


import asyncio
from llama_index.core.schema import QueryBundle
from dotenv import load_dotenv

from src.config import init_app_settings
from src.ingestion_events import IngestionWorkflow
from src.agent_events import AgentWorkFlow
from src.chat_ui import build_gradio_app



load_dotenv()

vector_store, storage_context, pinecone_index = init_app_settings()

query_engine = None
index=None


async def initialize_system():
    global query_engine, index

    # run ingestion
    ingestion = IngestionWorkflow(timeout=120)
    index = await ingestion.run(data_path="./data")

    if index is None:
        raise RuntimeError("Ingestion failed.")

    # build query engine via workflow
    qe_workflow = AgentWorkFlow(timeout=30)
    query_engine = await qe_workflow.run(index=index, top_k=7)
    print("System ready.")


async def async_query(question: str) -> tuple[str, list[dict]]:
    if(question==""):
        return "Oops! it seems you didn't send anything!", "no resources found"
    
    bundle = QueryBundle(query_str=question)
    response = await query_engine.aquery(bundle)

    answer = str(response)
    sources = []
    if hasattr(response, "source_nodes"):
        for node in response.source_nodes:
            sources.append({
                "score": round(node.score, 3) if node.score else "N/A",
                "text": node.node.get_content()[:300] + "...",
                "file": node.node.metadata.get("file_name", "unknown"),
            })
    return answer, sources


def run_query(question: str) -> tuple[str, str]:
    if(question==""):
        return "Oops! it seems you didn't send anything!", "no resources found"
    answer, sources = asyncio.run(async_query(question))
    if not sources:
        return answer, "_No sources found._"
    lines = ["### Sources"]
    for i, s in enumerate(sources, 1):
        lines.append(f"\n**{i}. {s['file']}** (score: {s['score']})\n> {s['text']}\n")
    return answer, "\n".join(lines)


def rebuild_engine(top_k: int, cutoff: float):
    # re-run the workflow with new params
    global query_engine
    qe_workflow = AgentWorkFlow(timeout=30)
    query_engine = asyncio.run(qe_workflow.run(
        index=index, top_k=top_k, cutoff=cutoff
    ))


if __name__ == "__main__":
    asyncio.run(initialize_system())

    app = build_gradio_app(
        run_query_fn=run_query,
        rebuild_engine_fn=rebuild_engine,
    )
    app.launch(server_name="0.0.0.0", server_port=7860)
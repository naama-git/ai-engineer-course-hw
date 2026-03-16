import asyncio

import concurrent
import netfree_patch
 
from llama_index.core import VectorStoreIndex
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import (
    SimilarityPostprocessor,
)
from llama_index.core.response_synthesizers import get_response_synthesizer, ResponseMode
from llama_index.core.schema import QueryBundle
 
from dotenv import load_dotenv
load_dotenv()

from chat_ui import build_gradio_app
from ingestion import ingestion_pipeline
from config import init_app_settings

vector_store, storage_context, pinecone_index = init_app_settings()

index = None
query_engine = None

def build_retriever(target_index,similarity_top_k: int = 5) -> VectorIndexRetriever:
    retriever = VectorIndexRetriever(
        index=target_index,
        similarity_top_k=similarity_top_k,
    )
    return retriever


def build_query_engine(target_index, similarity_top_k: int = 5, similarity_cutoff: float = 0.5):
    retriever = build_retriever(target_index, similarity_top_k)
    
    postprocessors = [
        SimilarityPostprocessor(similarity_cutoff=similarity_cutoff),
    ]
    
    synthesizer = get_response_synthesizer(
        response_mode=ResponseMode.SIMPLE_SUMMARIZE,
        use_async=True,
    )

    return RetrieverQueryEngine(
        retriever=retriever,
        node_postprocessors=postprocessors,
        response_synthesizer=synthesizer,
    )

async def async_query(question: str) -> tuple[str, list[dict]]:
    global query_engine
    bundle = QueryBundle(query_str=question)
    response = await query_engine.aquery(bundle)

    answer = str(response)
    sources = []
    if hasattr(response, "source_nodes"):
        for node in response.source_nodes:
            sources.append({
                "score": round(node.score, 3) if node.score else "N/A",
                "text":  node.node.get_content()[:300] + "...",
                "file":  node.node.metadata.get("file_name", "unknown"),
            })
    return answer, sources


def run_query(question: str) -> tuple[str, str]:
    with concurrent.futures.ThreadPoolExecutor() as pool:
        answer, sources = pool.submit(asyncio.run, async_query(question)).result()

    if not sources:
        return answer, "_Relevant sources not found._"

    lines = ["### 📚 Sources"]
    for i, s in enumerate(sources, 1):
        lines.append(f"\n**{i}. {s['file']}** (score: {s['score']})\n> {s['text']}\n")
    return answer, "\n".join(lines)

def _rebuild_engine(top_k: int, cutoff: float) -> None:
    global query_engine, index
    if index is None:
        print("Warning: index not initialized, cannot rebuild engine.")
        return
    query_engine = build_query_engine(index, similarity_top_k=top_k, similarity_cutoff=cutoff)

async def initialize_system():
    global index, query_engine

    index = await ingestion_pipeline()
    
    if index is None:
        print("Failed to initialize the system.")
        return False

    query_engine = build_query_engine(index)
    print("✅  ready !")
    return True

if __name__ == "__main__":
    if not asyncio.run(initialize_system()):
        print("Startup failed, exiting.")
        raise SystemExit(1)

    app = build_gradio_app(
        run_query_fn=run_query,
        rebuild_engine_fn=_rebuild_engine,
    )
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=True,
    )
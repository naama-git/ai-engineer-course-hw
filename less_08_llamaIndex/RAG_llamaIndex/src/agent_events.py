
import netfree_patch

from llama_index.core.workflow import Workflow, StartEvent ,StopEvent , Event, step , Context
 
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import (
    SimilarityPostprocessor,
)
from llama_index.core.response_synthesizers import get_response_synthesizer, ResponseMode
 
from dotenv import load_dotenv
load_dotenv()

from config import init_app_settings

vector_store, storage_context, pinecone_index = init_app_settings()


class BuildRetrieverEvent(Event):
    index: object
    top_k: int = 7

class BuildPostprocessorEvent(Event):
    retriever: object
    cutoff: float = 0.5

class BuildSynthesizerEvent(Event):
    retriever: object
    postprocessors: list


class AgentWorkFlow(Workflow):
    @step
    async def build_retriever(self, ev:StartEvent) ->BuildRetrieverEvent:
        return BuildRetrieverEvent(
            index=ev.index,
            top_k=ev.top_k or 7,
        )
    
    @step
    async def bulid_postprocessor(self, ev:BuildRetrieverEvent)->BuildPostprocessorEvent:
        retriever = VectorIndexRetriever(
            index=ev.index,
            similarity_top_k=ev.top_k,
        )
        return BuildPostprocessorEvent(
            retriever=retriever,
            cutoff=0.5,
        )
    
    @step
    async def build_synthesizer(self, ev: BuildPostprocessorEvent) -> BuildSynthesizerEvent:
        postprocessors = [SimilarityPostprocessor(similarity_cutoff=ev.cutoff)]
        return BuildSynthesizerEvent(
            retriever=ev.retriever,
            postprocessors=postprocessors,
        )

    @step
    async def build_query_engine(self, ev: BuildSynthesizerEvent) -> StopEvent:
        synthesizer = get_response_synthesizer(
            response_mode=ResponseMode.SIMPLE_SUMMARIZE,
            use_async=True,
        )
        engine = RetrieverQueryEngine(
            retriever=ev.retriever,
            node_postprocessors=ev.postprocessors,
            response_synthesizer=synthesizer,
        )
        return StopEvent(result=engine)

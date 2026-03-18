# ----- A helper class for running the Mongo search engine asynchronously
from llama_index.core.query_engine import CustomQueryEngine
from llama_index.core.workflow import Workflow

from src.mongo_query_events import MongoQueryWorkflow


class MongoWorkflowEngine(CustomQueryEngine):
    
    workflow: Workflow
    schema_id: str

    def custom_query(self, query_str: str):
    
        import asyncio
        return asyncio.run(self.workflow.run(query=query_str, schema_id=self.schema_id))

    async def acustom_query(self, query_str: str):
        return await self.workflow.run(query=query_str, schema_id=self.schema_id)

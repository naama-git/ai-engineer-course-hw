# ----- Mongo query engine. 
# ----- it gets a user question, prepares it into mongo query. executes it and returns the response to the user.

import json
from bson import ObjectId

import netfree_patch
from llama_index.core.workflow import Workflow, StartEvent, StopEvent, Event, step, Context
from llama_index.core.program import LLMTextCompletionProgram
from schemas import MongoQuery, RootSchema


class MongoSearchEvent(Event):
    query_obj: MongoQuery
    query:str


class MongoResultEvent(Event):
    results: list[dict]
    query:str


class MongoQueryWorkflow(Workflow):
    def __init__(self, mongo_collection, llm, **kwargs):
        super().__init__(**kwargs)
        self.collection = mongo_collection
        self.llm = llm
        self.schema_text = json.dumps(RootSchema.model_json_schema())

    @step
    async def prepare_query(self, ctx: Context, ev: StartEvent) -> MongoSearchEvent:
        schema_id = getattr(ev, "schema_id", await ctx.store.get("schemaId", default="default_schema"))
        query_str = ev.query

        schema_as_dict = RootSchema.model_json_schema()
        root_schema_json_str = json.dumps(schema_as_dict, indent=2)

        prompt = (
            f"You are a MongoDB expert. The database follows this schema:\n"
            f"{root_schema_json_str}\n\n"
            f"User query: '{query_str}'.\n"
            f"Instructions:\n"
            f"1. Use dot notation for nested fields (e.g., 'decisions.title').\n"
            f"2. Ensure the filter is a valid MongoDB JSON object.\n"
            f"3. If searching for text, use '$regex' with '$options': 'i' for better results.\n"
            f"4. Do NOT include '_id' or 'schemaId' in the filter."
        )

        program = LLMTextCompletionProgram.from_defaults(
            output_cls=MongoQuery,
            prompt_template_str="{prompt}",
            llm=self.llm
        )

        structured_output = await program.acall(prompt=prompt)

        if not structured_output.filter:
            structured_output.filter = {}

        structured_output.filter["_id"] = ObjectId(schema_id)

        print(f"--- Final Mongo Filter (Safety Applied): {structured_output.filter} ---")
        return MongoSearchEvent(query_obj=structured_output , query=query_str)

    @step
    async def execute_search(self, ev: MongoSearchEvent) -> MongoResultEvent:
        query_filter = ev.query_obj.filter
        limit = getattr(ev.query_obj, "limit", 5)

        print(f"DEBUG: Executing find with filter: {query_filter} on collection: {self.collection}")

        cursor = self.collection.find(query_filter).limit(limit)
        results = await cursor.to_list(length=limit)

        print(f"DEBUG: Found {len(results)} results")
        return MongoResultEvent(results=results,query=ev.query)

    @step
    async def synthesize_response(self, ev: MongoResultEvent) -> StopEvent:
        if not ev.results:
            return StopEvent(result="Relevant results were not found in DB")

        prompt = (
                f"User question: '{ev.query}'\n\n"
                f"Relevant data from the DB:\n{ev.results}\n\n"
                f"Answer the question directly and concisely. "
                f"Do not dump all the data — only mention what is relevant to the question."
        )

        summary = await self.llm.acomplete(prompt)
        return StopEvent(result=str(summary))
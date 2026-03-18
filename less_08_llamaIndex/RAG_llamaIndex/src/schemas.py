# -------- Pydantic schemas to define the JSON data to the LLM

import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

class General(BaseModel):
    id: str = Field(description="Unique scan/session ID")
    version: str = Field(default="1.0", description="Schema version")
    generated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)


class LinesRange(BaseModel):
    start:int=Field("Start line")
    end:int=Field("End line")

class Decision(BaseModel):
    id: str = Field(description="Unique decision ID (e.g., 'dec-001')")
    title: str = Field(description="Short title of the decision")
    description: str = Field(description="Detailed rationale and context")
    source_file: str = Field(description="Path to the source file")
    lines_range: LinesRange= Field(description="Line range. for example: {start: 50 , end:100}")
    tags: List[str] = Field(default_factory=list, description="Classification tags")


class Change(BaseModel):
    id: str = Field(description="Unique change ID")
    change: str = Field(description="Summary of the modification")
    before: str = Field(description="State before the change")
    after: str = Field(description="State after the change")
    tool: str = Field(description="Tool used (e.g., 'cursor', 'claude')")
    source_file: str = Field(description="File where change is documented")
    lines_range:LinesRange = Field(description="Line range. for example: {start: 50 , end:100}")
    tags: List[str] = Field(default_factory=list)
    date: datetime.datetime = Field(description="Timestamp of the change")

class Rule(BaseModel):
    id: str = Field(description="Unique rule ID (e.g., 'rule-001')")
    rule: str = Field(description="The formal rule or instruction")
    severity: Literal["low", "medium", "high"] = Field(description="Criticality level")
    source_file: str = Field(description="File defining the rule")
    lines_range: LinesRange = Field(description="Line range. for example: {start: 50 , end:100}")
    tags: List[str] = Field(default_factory=list)


class RootSchema(BaseModel):
    metadata: General = Field(description="General scan information")
    decisions: List[Decision] = Field(default_factory=list, description="List of all architectural decisions found")
    changes: List[Change] = Field(default_factory=list, description="List of all recorded changes")
    rules: List[Rule] = Field(default_factory=list, description="List of all coding rules and constraints")




class MongoQuery(BaseModel):
    model_config = ConfigDict(
        extra='ignore'
    )
    filter: dict = Field(
        description="""MongoDB filter object. 
        IMPORTANT: The data is nested. Use dot notation:
        - For decisions: 'decisions.title', 'decisions.description', 'decisions.tags'
        - For rules: 'rules.rule', 'rules.severity'
        - For changes: 'changes.change', 'changes.tool'
        Example: {'decisions.tags': 'architecture'}"""
    )
    limit: int = Field(default=5, description="Number of records to return")
    sort_by: Optional[str] = Field(description="Field name to sort by, e.g. 'processed_at'")
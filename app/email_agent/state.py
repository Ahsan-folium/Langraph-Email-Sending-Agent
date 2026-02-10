from typing import Literal, Optional, TypedDict
from langgraph.graph import MessagesState
import operator
from typing import Annotated, TypedDict
from langchain_core.messages import AnyMessage


class EmailState(TypedDict):
    subject: str
    tone: Optional[Literal["formal", "casual", "friendly"]]
    generated_email: Optional[str]
    messages: Annotated[list[AnyMessage], operator.add]

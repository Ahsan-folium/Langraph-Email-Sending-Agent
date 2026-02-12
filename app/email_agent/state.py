from typing import Literal, Optional, TypedDict
import operator
from typing import Annotated
from langchain_core.messages import AnyMessage


class EmailState(TypedDict):
    recepient: str
    subject: str
    tone: Optional[Literal["formal", "casual", "friendly"]]
    messages: Annotated[list[AnyMessage], operator.add]
    generated_email: Optional[str]
    draft: Optional[str]

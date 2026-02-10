from pydantic import BaseModel, EmailStr


# routes
class EmailRequestBody(BaseModel):
    recepient: str
    subject: str
    tone: str
    # messages: Annotated[list[AnyMessage], operator.add]


class EmailResponseBody(BaseModel):
    generated_email: str


# models for functions

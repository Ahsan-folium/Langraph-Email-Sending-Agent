from pydantic import BaseModel, EmailStr


# routes
class EmailRequestBody(BaseModel):
    recepient: str
    subject: str
    tone: str


class ApproveEmailRequest(BaseModel):
    thread_id: str
    draft: str


class EmailResponseBody(BaseModel):
    generated_email: str

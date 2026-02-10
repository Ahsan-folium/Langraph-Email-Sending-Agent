from fastapi import APIRouter

from app.email_agent.client import EmailAgentGraph
from app.email_agent.schema import EmailRequestBody, EmailResponseBody

api_file_router = APIRouter(tags=["health"])


@api_file_router.get("/health")
def health():
    return {"status": "ok"}


@api_file_router.get("/health2")
def health2():
    return {"status": "okay by health 2"}


# we make an instance of the email agent
email_agent = EmailAgentGraph()


@api_file_router.post("/send_email")
def sendMail(input: EmailRequestBody):
    result = email_agent.invoke(input)
    print("+" * 200)
    print(result)
    print("+" * 200)

    response = {
        "subject": result.get("subject"),
        "tone": result.get("tone"),
        "email": result["messages"][-1].content,
    }
    return {"message": response}

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.email_agent.client import EmailAgentGraph
from app.email_agent.schema import EmailRequestBody, EmailResponseBody

api_file_router = APIRouter(tags=["health"])


@api_file_router.get("/health")
def health():
    return JSONResponse(status_code=200, content={"success": True, "status": "ok"})


# we make an instance of the email agent
email_agent = EmailAgentGraph()


@api_file_router.post("/send_email")
def sendMail(input: EmailRequestBody):
    try:
        result = email_agent.invoke(input)
        print("+" * 200)
        print(result)
        print("+" * 200)
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "success": False,
                "error": "Email agent failed",
                "message": str(e),
            },
        )

    response = {
        "recepient": result.get("recepient"),
        "subject": result.get("subject"),
        "tone": result.get("tone"),
        "email": result["messages"][-1].content,
    }
    return {"message": response}

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.email_agent.client import EmailAgentGraph
from app.email_agent.schema import EmailRequestBody
from app.routes.helpers import get_sent_email_body

api_file_router = APIRouter(tags=["health"])


@api_file_router.get("/health")
def health():
    return JSONResponse(
        status_code=200,
        content={"success": True, "status": "ok"},
    )


email_agent = EmailAgentGraph()


@api_file_router.post("/send_email")
def send_mail(input: EmailRequestBody):
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

    messages = result.get("messages") or []
    if not messages:
        raise HTTPException(
            status_code=503,
            detail={
                "success": False,
                "error": "No response from email agent",
            },
        )

    email_body = get_sent_email_body(messages)
    if email_body is None:
        raise HTTPException(
            status_code=503,
            detail={
                "success": False,
                "error": "Could not determine sent email content",
            },
        )

    response_data = {
        "recepient": result.get("recepient"),
        "subject": result.get("subject"),
        "tone": result.get("tone"),
        "email": email_body,
    }

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": "Email sent successfully",
            "data": response_data,
        },
    )

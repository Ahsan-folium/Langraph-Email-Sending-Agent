import uuid

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.email_agent.client import EmailAgentGraph
from app.email_agent.schema import ApproveEmailRequest, EmailRequestBody
from app.routes.helpers import get_draft_from_interrupt

api_file_router = APIRouter(tags=["health"])


@api_file_router.get("/health")
def health():
    return JSONResponse(
        status_code=200,
        content={"success": True, "status": "ok"},
    )


email_agent = EmailAgentGraph()


@api_file_router.post("/generate_email")
def generate_email(input: EmailRequestBody):
    """Generate a draft email. Returns the draft for human review."""
    thread_id = str(uuid.uuid4())
    try:
        result = email_agent.invoke(input, thread_id=thread_id)
        print("*" * 100)
        print(f"result from first invoke : {result}")
        print("*" * 100)
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "success": False,
                "error": "Email agent failed",
                "message": str(e),
            },
        )

    draft = get_draft_from_interrupt(result)
    if draft is None:
        raise HTTPException(
            status_code=503,
            detail={
                "success": False,
                "error": "Could not extract draft from agent response",
            },
        )

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": "Draft generated — review and approve",
            "data": {
                "thread_id": thread_id,
                "recepient": input.recepient,
                "subject": input.subject,
                "tone": input.tone,
                "draft": draft,
            },
        },
    )


@api_file_router.post("/approve_email")
def approve_email(input: ApproveEmailRequest):
    """Resume the graph with the reviewed/edited draft and send."""
    try:
        result = email_agent.resume(input.thread_id, input.draft)
        print("#" * 100)
        print(f"result from second invoke : {result}")
        print("#" * 100)
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "success": False,
                "error": "Email send failed",
                "message": str(e),
            },
        )

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": "Email sent successfully",
            "data": {
                "generated_email": result.get("generated_email"),
                "recepient": result.get("recepient"),
                "subject": result.get("subject"),
                "tone": result.get("tone"),
            },
        },
    )

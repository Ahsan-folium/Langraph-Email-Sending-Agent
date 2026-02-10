from langchain_core.tools import tool
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


@tool
def calculator(first_num: float, second_num: float, operation: str) -> dict:
    """
    Perform a basic arithmetic operation on two numbers.
    Supported operations: add, sub, mul, div
    """
    try:
        if operation == "add":
            result = first_num + second_num
        elif operation == "sub":
            result = first_num - second_num
        elif operation == "mul":
            result = first_num * second_num
        elif operation == "div":
            if second_num == 0:
                return {"error": "Division by zero is not allowed"}
            result = first_num / second_num
        else:
            return {"error": f"Unsupported operation '{operation}'"}

        return {
            "first_num": first_num,
            "second_num": second_num,
            "operation": operation,
            "result": result,
        }
    except Exception as e:
        return {"error": str(e)}


@tool
def send_email(to: str, subject: str, body: str) -> dict:
    """
    Send an email to the given recipient.
    Uses SMTP credentials from env: SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD.
    """
    host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    if not user or not password:
        return {"error": "SMTP_USER and SMTP_PASSWORD must be set in environment"}
    try:
        msg = MIMEMultipart()
        msg["From"] = user
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        with smtplib.SMTP(host, port) as server:
            server.starttls()
            server.login(user, password)
            server.sendmail(user, to, msg.as_string())
        return {"ok": True, "to": to, "subject": subject}
    except Exception as e:
        return {"error": str(e)}

from langchain_core.messages import AIMessage


def get_sent_email_body(messages: list) -> str | None:
    for msg in reversed(messages):
        if not isinstance(msg, AIMessage) or not getattr(msg, "tool_calls", None):
            continue
        for tc in msg.tool_calls:
            name = tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", None)
            if name == "send_email":
                args = (
                    tc.get("args")
                    if isinstance(tc, dict)
                    else getattr(tc, "args", None)
                )
                args = args if isinstance(args, dict) else {}
                return args.get("body")
    return None

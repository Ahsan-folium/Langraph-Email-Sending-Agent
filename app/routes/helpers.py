from langgraph.types import Interrupt


def get_draft_from_interrupt(result: dict) -> str | None:
    """Extract the draft email from the graph's __interrupt__ payload."""
    interrupts = result.get("__interrupt__")
    if not interrupts:
        return None

    for item in interrupts:
        if isinstance(item, Interrupt) and isinstance(item.value, dict):
            return item.value.get("draft")

    return None

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import Command, interrupt
from langgraph.checkpoint.sqlite import SqliteSaver

from app.email_agent.prompt import (
    EMAIL_GENERATION_HUMAN_PROMPT,
    EMAIL_GENERATION_SYSTEM_PROMPT,
)
from app.email_agent.state import EmailState
from app.email_agent.tools import search_tool, send_email
from dotenv import load_dotenv
import sqlite3
import os

load_dotenv()

DUMMY_THREAD_ID = "email-thread-1"


class EmailAgentGraph:
    def __init__(self, model_name="gpt-5-nano"):
        def _get_openai_api_key():
            return os.getenv("OPENAI_API_KEY", "")

        # Only search_tool is bound to the model.
        # send_email is called programmatically after human approval.
        self.tools = [search_tool]
        self.model = ChatOpenAI(
            model=model_name, api_key=_get_openai_api_key
        ).bind_tools(self.tools)
        self.tool_node = ToolNode(self.tools)

        conn = sqlite3.connect("checkpoints.sqlite", check_same_thread=False)
        self.checkpointer = SqliteSaver(conn=conn)

    # ── nodes ────────────────────────────────────────────────

    def _generate_email(self, state: EmailState):
        system_msg = SystemMessage(content=EMAIL_GENERATION_SYSTEM_PROMPT)

        if not state["messages"]:
            human_msg = HumanMessage(
                content=EMAIL_GENERATION_HUMAN_PROMPT.format(
                    subject=state.get("subject"),
                    tone=state.get("tone"),
                    recipient=state.get("recepient", ""),
                )
            )
            response = self.model.invoke([system_msg, human_msg])
            return {"messages": [human_msg, response]}

        response = self.model.invoke([system_msg] + state["messages"])
        return {"messages": [response]}

    def _human_review(self, state: EmailState):
        """Pause here so the user can review / edit the draft."""
        draft = state["messages"][-1].content
        reviewed_draft = interrupt({"draft": draft})
        return {"draft": reviewed_draft}

    def _send_email(self, state: EmailState):
        """Send the approved (possibly edited) draft via SMTP."""
        draft = state["draft"] or ""
        send_email(
            to=state["recepient"],
            subject=state["subject"],
            body=draft,
        )
        return {"generated_email": draft}

    # ── graph ────────────────────────────────────────────────

    def _build_graph(self):
        graph = StateGraph(EmailState)

        graph.add_node("email_generation_node", self._generate_email)
        graph.add_node("tools", self.tool_node)
        graph.add_node("human_review", self._human_review)
        graph.add_node("send_email_node", self._send_email)

        graph.add_edge(START, "email_generation_node")

        graph.add_conditional_edges(
            "email_generation_node",
            tools_condition,
            {"tools": "tools", "__end__": "human_review"},
        )

        graph.add_edge("tools", "email_generation_node")

        graph.add_edge("human_review", "send_email_node")
        graph.add_edge("send_email_node", END)

        return graph.compile(checkpointer=self.checkpointer)

    # ── public API ───────────────────────────────────────────

    def invoke(self, input_data, thread_id: str = DUMMY_THREAD_ID):
        """Start the graph — runs until interrupt, returns draft."""
        initial_state = {
            "messages": [],
            **input_data.model_dump(),
        }
        config = {"configurable": {"thread_id": thread_id}}
        graph = self._build_graph()

        return graph.invoke(initial_state, config)  # pyright: ignore[reportArgumentType]

    def resume(self, thread_id: str, edited_draft: str):
        """Resume the graph after human review — sends the email."""
        config = {"configurable": {"thread_id": thread_id}}
        graph = self._build_graph()

        return graph.invoke(Command(resume=edited_draft), config)  # pyright: ignore[reportArgumentType]

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from app.email_agent.prompt import (
    EMAIL_GENERATION_HUMAN_PROMPT,
    EMAIL_GENERATION_SYSTEM_PROMPT,
)
from app.email_agent.schema import EmailResponseBody
from app.email_agent.state import EmailState
from dotenv import load_dotenv
import os

from app.email_agent.tools import calculator

load_dotenv()


class EmailAgentGraph:
    def __init__(self, model_name="gpt-5-nano"):
        def _get_openai_api_key():
            return os.getenv("OPENAI_API_KEY", "")

        self.tools = [calculator]
        self.model = ChatOpenAI(
            model=model_name, api_key=_get_openai_api_key
        ).bind_tools(self.tools)
        self.tool_node = ToolNode(self.tools)

    def _generate_email(self, state: EmailState):
        system_msg = SystemMessage(content=EMAIL_GENERATION_SYSTEM_PROMPT)

        if not state["messages"]:
            human_msg = HumanMessage(
                content=EMAIL_GENERATION_HUMAN_PROMPT.format(
                    subject=state.get("subject"),
                    tone=state.get("tone"),
                )
            )
            messages = [system_msg, human_msg]
        else:
            messages = [system_msg] + state["messages"]

        response = self.model.invoke(messages)
        return {"messages": [response]}

    def _build_graph(self):
        graph = StateGraph(EmailState)
        graph.add_node("email_generation_node", self._generate_email)
        # node with tools
        graph.add_node("tools", self.tool_node)

        graph.add_edge(START, "email_generation_node")
        graph.add_conditional_edges("email_generation_node", tools_condition)
        graph.add_edge("tools", "email_generation_node")
        # graph.add_edge("email_generation_node", END)

        return graph.compile()

    def invoke(self, input_data):
        # initial_state = input_data
        input_data = input_data.model_dump()
        initial_state = {
            "messages": [],  # Start with empty messages
            **input_data,  # subject, tone
        }
        graph = self._build_graph()

        return graph.invoke(initial_state)

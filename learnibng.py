from dotenv import load_dotenv
from typing import Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field 
from typing_extensions import TypedDict

import os

load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

llm = ChatGroq(api_key=API_KEY, model="llama-3.3-70b-versatile", temperature=0.7)


class MessageClassifier(BaseModel):
    message_type: Literal["emotional","logical"] = Field(
        ..., description="Classify what type the message will be"
    )
class State(TypedDict):
    messages: Annotated[list, add_messages]
    message_type: str|None



def classify_message(state: State):
    last_message = state["messages"][-1]
    classifier_llm=llm.with_structured_output(MessageClassifier)

    result = classifier_llm.invoke([
        {"role":"system","content":"Classify the following message as either emotional or logical"},
        {"role":"user","content":last_message.content}
    ])

    return {"message_type": result.message_type}

        

def router(state:State):
    message_type = state.get("message_type",'logical')
    if message_type == "emotional":
        return {"next":"therapist"}
    
    return {"next":"logical"}

def therapist_agent(state: State):
    last_message = state["messages"][-1]

    messages = [
        {
            "role":"system",
            "content":"You are a compassionate therapist. Respond to the user's message with empathy and understanding."
        },
        {
            "role":"user",
            "content": last_message.content

        }
    ]

    reply = llm.invoke(messages)
    return {'messages':[{"role":"assistant","content":reply.content}]}

def logical_agent(state: State):
    last_message = state["messages"][-1]

    messages = [
        {
            "role":"system",
            "content":"You are a logical agent. Respond to the user's message with clear and rational thinking."
        },
        {
            "role":"user",
            "content": last_message.content

        }
    ]

    reply = llm.invoke(messages)
    return {'messages':[{"role":"assistant","content":reply.content}]}

graph_builder = StateGraph(State)

graph_builder.add_node("classifier", classify_message)
graph_builder.add_node("router", router)
graph_builder.add_node("therapist", therapist_agent)
graph_builder.add_node("logical", logical_agent)
graph_builder.add_edge(START, "classifier")
graph_builder.add_edge("classifier", "router")
graph_builder.add_conditional_edges(
    "router",
    lambda state: state.get("next"),
    path_map={"therapist":"therapist","logical":"logical"}
)
graph_builder.add_edge("therapist", END)
graph_builder.add_edge("logical", END)

graph = graph_builder.compile()

def run_chatbot():
    state = {"messages": [], "message_type": None}

    while True:
        user_input = input("Message: ")
        if user_input == "exit":
            print("Bye")
            break

        state["messages"] = state.get("messages", []) + [
            {"role": "user", "content": user_input}
        ]

        state = graph.invoke(state)

        if state.get("messages") and len(state["messages"]) > 0:
            last_message = state["messages"][-1]
            print(f"Assistant: {last_message.content}")


if __name__ == "__main__":
    run_chatbot()
from typing import TypedDict, List
from dotenv import load_dotenv
import os
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field
from fastapi import FastAPI

load_dotenv()

class State(TypedDict):
    field: str
    task: str
    steps: List[str]

class Step(BaseModel):
    steps: List[str]

class AgentRequest(BaseModel):
    field: str = Field(description="The field of interest")
    task: str = Field(description="The task to accomplish")


class AgentResponse(BaseModel):
    steps: List[str]

#---Nodes-----------------------------------------------------------------------------------------------------------------------------------
llm = ChatOllama(model=os.getenv('MODEL'))

prompt = ChatPromptTemplate.from_template(
    '''
        You are an expert in {field}

        The user wants to accomplish their task of {task}

        Give them step by step guide on how to accomplish it.
    '''

)

def give_steps(State) -> dict:
    print('Breaking down task...')
    message = prompt.invoke({'field' : State['field'], 'task' : State['task']})

    print(message)
    
    structured_llm = llm.with_structured_output(Step)
    response = structured_llm.invoke(message)

    return {'steps' : response.steps}

#---Graph-----------------------------------------------------------------------------------------------------------------------------------

builder = StateGraph(State)

builder.add_node('give_steps', give_steps)

builder.add_edge(START, 'give_steps')
builder.add_edge('give_steps', END)

graph = builder.compile()

#---FastAPI-----------------------------------------------------------------------------------------------------------------------------------

app = FastAPI()

@app.post("/run-agent", response_model=AgentResponse)
async def run_agent(request: AgentRequest):

    result = graph.invoke({"field": request.field, "task": request.task})
    return {"steps": result["steps"]}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
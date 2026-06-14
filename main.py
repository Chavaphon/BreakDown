
import re
from typing import TypedDict, Optional, List, Literal
from dotenv import load_dotenv
import os
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field

load_dotenv()

class State(TypedDict):
    field: str
    task: str
    steps: List[str]

class Step(BaseModel):
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

#---Start-----------------------------------------------------------------------------------------------------------------------------------

builder = StateGraph(State)

builder.add_node('give_steps', give_steps)

builder.add_edge(START, 'give_steps')
builder.add_edge('give_steps', END)

graph = builder.compile()

field = input('What is your field of interest?')
task = input('What is your task?')

respond = graph.invoke({'field' : field, 'task': task})

print(respond)
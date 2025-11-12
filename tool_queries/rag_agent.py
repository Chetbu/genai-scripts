import os
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional

from pydantic import BaseModel, Field

from langgraph.checkpoint.memory import MemorySaver

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from openai import AsyncAzureOpenAI


from pathlib import Path

script_name = Path(__file__).stem
current_dir = str(Path(__file__).parent)

default_d: dict = {
    'max_iteration': 2,
    'generation_llm_model_name': '',
    'embedding_model_name': '',
    'research_llm_model_name': '',
    'critique_llm_model_name': ''
}

def pydantic_agent(llm_model_name: str, system_prompt_str: str = ""):
    api_key=os.getenv("AZURE_OPENAI_API_KEY")
    api_version=os.getenv("OPENAI_API_VERSION")
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")

    client = AsyncAzureOpenAI(
        azure_endpoint=azure_endpoint,
        api_version=api_version,
        api_key=api_key,
    )
    model = OpenAIModel(
        llm_model_name,
        provider=OpenAIProvider(openai_client=client),
    )
    agent = Agent(
        model,
        system_prompt=system_prompt_str,
        )
    return agent

class RAGDocument(TypedDict):
    """Format of processed documents for RAG"""

    content: str
    metadata: dict = {}

class RAGAgentParam:
    max_iteration: int
    generation_llm_model_name: str
    embedding_model_name: str
    research_llm_model_name: str
    critique_llm_model_name: str

    def __init__(self, d=None):
        if d is None:
            d = default_d
        for key, value in d.items():
            setattr(self, key, value)


async def rag_agent(research_task: str, conversation_id: str, param: RAGAgentParam, user_email: str):
    # RAG agent using internal knowledge base

    max_iteration = param.max_iteration
    generation_llm_model_name = param.generation_llm_model_name
    embedding_model_name = param.embedding_model_name
    research_llm_model_name = param.research_llm_model_name
    critique_llm_model_name = param.critique_llm_model_name

    memory = MemorySaver()

    class QuestionAnswer(TypedDict):
        question : str
        answer : Optional[str]

    class AgentState(TypedDict):
        task: str  # human ask
        critique: Optional[str]  # Output of critique
        content: List[RAGDocument] #documents provided by internal search
        answer: Optional[str] #final answer of the model
        revision_number: int
        max_revisions: int
        user_email: str
        embedding_model_name : str
        research_questions_and_answers: list[QuestionAnswer] #questions generated for the research


    #Prompt for the RAG
    QA_PROMPT_TEMPLATE = """
    You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. 
    If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.

    Question: {question}

    Context: {context}

    """

    
    REFLECTION_PROMPT = """You are a teacher grading an essay submission. \
    Generate critique and recommendations for the user's submission. \
    Provide detailed recommendations, including requests for length, depth, style, etc."""
    
    RESEARCH_PROMPT = """You are an expert research assistant. Your job is to generate questions that can help you find information. \
    You need to provide the question that would best help you to find information about the following user request.
    You need to provide it under a json format list.

    """

    RESEARCH_AFTER_CRITIQUE_PROMPT = """You are an expert research assistant. Your job is to generate questions that can help you find information. \
    You need to provide the question that would best help you to find information about the following user request.
    You need to provide it under a json format list.

    You will be provided with the list of questions already identified. Please make sure that you dont have too much overlap between the exisiting questions and the new questions \
    You will also be provided with a critique from an expert on the existing state of the answer. Please use it to generate new relevant questions and improve the answer

    """

    SYNTHESIS_PROMPT = """You are an expert writer. You will be given a list of questions and answers that were answered by expert using internal documentation and the initial ask by the user
    Your job will be to use the questions and answers of write a synthetic answer to the initial ask by the user

    """

    class ResearchQuestions(BaseModel):
        questions: List[str] = Field(description="List of questions to use for the research")


    async def research_node(state: AgentState):
        #large_model
        agent = pydantic_agent(
            generation_llm_model_name,
            system_prompt_str=RESEARCH_PROMPT
            )
        
        response = await agent.run(
            state['task'],
            result_type=ResearchQuestions,
            )

        qa_list : list[QuestionAnswer] = []

        if "research_questions_and_answers" in state and len(state["research_questions_and_answers"]) > 0:
            qa_list = state["research_questions_and_answers"]

        for question in response.data.questions:
            qa_list.append({
                "question" : question,
                "answer" : None
            })


        return {"research_questions_and_answers": qa_list}
    
    async def research_after_critique_node(state: AgentState):
        human_prompt : str = "<initial_user_ask>" + state["task"] + "</initial_user_ask> \n"
        human_prompt += "<critique>" + state["critique"] + "</critique> \n"

        for qa in state["research_questions_and_answers"]:
            qa_str : str = "<question>" + qa["question"] + "</question> \n"
            human_prompt += qa_str

        #large_model
        agent = pydantic_agent(
            generation_llm_model_name,
            system_prompt_str=RESEARCH_AFTER_CRITIQUE_PROMPT
            )

        response = await agent.run(
            human_prompt,
            result_type=ResearchQuestions,
            )

        qa_list : list[QuestionAnswer] = []

        if "research_questions_and_answers" in state and len(state["research_questions_and_answers"]) > 0:
            qa_list = state["research_questions_and_answers"]

        for question in response.data.questions:
            qa_list.append({
                "question" : question,
                "answer" : None
            })


        return {"research_questions_and_answers": qa_list}

    async def rag_node(state: AgentState):
        
        retriever = get_user_pg_retriever(state['user_email'], state['embedding_model_name'])
        #small_model
        agent = pydantic_agent(
            research_llm_model_name,
            
            )

        qa_list : list[QuestionAnswer] = []

        if "research_questions_and_answers" in state and len(state["research_questions_and_answers"]) > 0:
            for qa in state["research_questions_and_answers"]:
                if qa["answer"] is None:
                    similary_search_result = retriever(qa["question"])
                    context_full_str = '\n\n'.join([x['content'] for x in similary_search_result])

                    full_prompt= QA_PROMPT_TEMPLATE.format(context=context_full_str, question=qa["question"])

                    answer = await agent.run(full_prompt)
                    
                    
                    res : QuestionAnswer = {
                        "question" : qa["question"],
                        "answer" : answer.data
                    }
                    qa_list.append(res)
                else:
                    qa_list.append(qa)
        else :
            raise Exception("No research questions found")
       
        return {
            "revision_number": state.get("revision_number", 1) + 1,
            "research_questions_and_answers": qa_list
        }
    
    async def synthesis_node(state: AgentState):
        qa_list : list[QuestionAnswer] = state["research_questions_and_answers"]

        human_prompt : str = "<initial_user_ask>" + state["task"] + "</initial_user_ask> \n"

        for qa in qa_list:
            qa_str : str = "<question>" + qa["question"] + "</question>" + "<answer>" + qa["answer"] + "</answer> \n"
            human_prompt += qa_str

        #large_model
        agent = pydantic_agent(
            generation_llm_model_name,
            system_prompt_str=SYNTHESIS_PROMPT
            )

        response = await agent.run(human_prompt)
        return {"answer": response.data}

    async def reflection_node(state: AgentState):
        #critique_model
        agent = pydantic_agent(
            critique_llm_model_name,
            system_prompt_str=REFLECTION_PROMPT
            )
            
        response = await agent.run(state['answer'])
        return {"critique": response.data}

    def should_continue(state):
        if state["revision_number"] > state["max_revisions"]:
            return END
        else:
            return "reflect"

    builder = StateGraph(AgentState)

    builder.add_node("research", research_node)
    builder.add_node("research_after_critique", research_after_critique_node)
    builder.add_node("rag", rag_node)
    builder.add_node("synthesis", synthesis_node)
    builder.add_node("reflect", reflection_node)

    builder.set_entry_point("research")

    builder.add_conditional_edges(
        "synthesis",
        should_continue,
        {END: END, "reflect": "reflect"}
    )
    builder.add_edge("research", "rag")
    builder.add_edge("research_after_critique", "rag")
    builder.add_edge("rag", "synthesis")

    builder.add_edge("reflect", "research_after_critique")


    graph = builder.compile(checkpointer=memory)

    # img = graph.get_graph().draw_mermaid_png()

    # output_file = Path(current_dir, script_name + "graph" + ".png")
    # with open(output_file, "wb") as png:
    #     png.write(img)

    thread = {"configurable": {"thread_id": conversation_id}}
    async for s in graph.astream({
        'task': research_task,
        "max_revisions": max_iteration,
        "revision_number": 1,
        "user_email": user_email,
        "embedding_model_name" : embedding_model_name
    }, thread):
        yield s

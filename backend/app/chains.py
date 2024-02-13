from .templates import (
    RETRIEVAL_PROMPT,
    SALES_PROMPT,
    CONDENSE_QUESTION_PROMPT,
    combine_docs,
)
from operator import itemgetter
from typing import Dict

from langchain_openai import ChatOpenAI
from langchain.schema import format_document
from langchain_core.messages import AIMessage, HumanMessage, get_buffer_string
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI


def build_pinecone_retrieval_chain(
    vectorstore,
) -> Dict:
    retriever = vectorstore.as_retriever()
    llm = ChatOpenAI(model_name="gpt-4-0125-preview", temperature=0, verbose=True)

    rag_chain_from_docs = (
        RunnablePassthrough.assign(context=(lambda x: combine_docs(x["context"])))
        | RETRIEVAL_PROMPT
        | llm
        | StrOutputParser()
    )

    rag_chain_with_source = RunnableParallel(
        {"context": retriever, "question": RunnablePassthrough()}
    ).assign(answer=rag_chain_from_docs)

    return rag_chain_with_source


def build_conversational_retrieval_chain(
    collection_name,
    user_retrieval_prompt=None,
) -> Dict:
    """
    Args:
        - collection_name: vectorstore로 사용할 collection 이름
        - user_retrieval_prompt: custom retrieval prompt template
    """
    if user_retrieval_prompt is None:
        user_retrieval_prompt = RETRIEVAL_PROMPT
    # persistent_client = chromadb.PersistentClient("backend/database/vectorstore/chroma")
    vectorstore = Chroma(
        persist_directory="backend/database/vectorstore/chroma",
        # client=persistent_client,
        collection_name=collection_name,
        embedding_function=OpenAIEmbeddings(),
    )
    print(f"💥Collection found w/ {vectorstore._collection.count()} document(s).")
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    llm = ChatOpenAI(model_name="gpt-4-0125-preview", temperature=0, verbose=True)

    inputs = RunnableParallel(
        standalone_question=RunnablePassthrough.assign(
            chat_history=lambda x: get_buffer_string(x["chat_history"])
        )
        | CONDENSE_QUESTION_PROMPT
        | ChatOpenAI(model_name="gpt-3.5-turbo-1106", temperature=0)
        | StrOutputParser()
    )

    retrieved_docs = {
        "docs": itemgetter("standalone_question") | retriever,
        "question": lambda x: x["standalone_question"],
    }

    final_inputs = {
        "context": lambda x: combine_docs(x["docs"]),
        "question": itemgetter("question"),
    }

    answer = {
        "answer": final_inputs | user_retrieval_prompt | llm,
        "docs": itemgetter("docs"),
        "standalone_question": itemgetter("question"),
    }

    conversational_retrieval_chain = inputs | retrieved_docs | answer
    return conversational_retrieval_chain


def build_conversational_chain(llm) -> Dict:
    inputs = {
        "chat_history": lambda x: get_buffer_string(x["chat_history"]),
        "question": itemgetter("question"),
    }

    conversational_chain = inputs | CONDENSE_QUESTION_PROMPT | llm
    return conversational_chain


def build_sales_chain(sales_prompt=None):
    _sales_prompt = sales_prompt or SALES_PROMPT
    llm = ChatOpenAI(model_name="gpt-4-0125-preview", temperature=0.3, verbose=True)
    sales_chain = _sales_prompt | llm
    return sales_chain


# inputs = RunnableParallel(
#     standalone_question=RunnablePassthrough.assign(
#         chat_history=lambda x: get_buffer_string(x["chat_history"])
#     )
#     | CONDENSE_QUESTION_PROMPT
#     | ChatOpenAI(model_name="gpt-3.5-turbo-1106", temperature=0)
#     | StrOutputParser()
# )


# retrieved_docs = {
#     "docs": itemgetter("standalone_question") | retriever,
#     "question": lambda x: x["standalone_question"],
# }

# final_inputs = {
#     "context": lambda x: combine_docs(x["docs"]),
#     "question": itemgetter("question"),
# }

# answer = {
#     "answer": final_inputs | retrieval_prompt | llm,
#     "docs": itemgetter("docs"),
# }

# conversational_retrieval_chain = inputs | retrieved_docs | answer

# print(conversational_retrieval_chain.get_prompts())
# conversational_retrieval_chain = build_conversational_retrieval_chain()
# resp = conversational_retrieval_chain.invoke(
#     {
#         "question": "미궁365 보관 방법은?",
#         "chat_history": [],
#     }
# )
# print(resp["answer"])
# for doc in resp["docs"]:
# print(doc)

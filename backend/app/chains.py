import chromadb

from .templates import retrieval_prompt, condense_question_prompt, combine_docs
from operator import itemgetter
from langchain_openai import ChatOpenAI
from langchain.schema import format_document
from langchain_core.messages import AIMessage, HumanMessage, get_buffer_string
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI


persistent_client = chromadb.PersistentClient(
    "/home/onejelly/workspace/prompt-engineering/backend/database/vectorstore/chroma"
)
vectorstore = Chroma(
    client=persistent_client,
    collection_name="test-0128",
    embedding_function=OpenAIEmbeddings(),
)
retriever = vectorstore.as_retriever()
llm = ChatOpenAI(
    model_name="gpt-4-0125-preview", temperature=0, max_tokens=200, verbose=True
)

# retrieval_chain = (
#     {"context": retriever, "question": RunnablePassthrough()}
#     | retrieval_prompt
#     | llm
#     | StrOutputParser()
# )

inputs = RunnableParallel(
    standalone_question=RunnablePassthrough.assign(
        chat_history=lambda x: get_buffer_string(x["chat_history"])
    )
    | condense_question_prompt
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
    "answer": final_inputs | retrieval_prompt | llm,
    "docs": itemgetter("docs"),
}

conversational_retrieval_chain = inputs | retrieved_docs | answer

resp = conversational_retrieval_chain.invoke(
    {
        "question": "미궁365 보관 방법은?",
        "chat_history": [],
    }
)
# print(resp["answer"])
# print(resp["docs"])

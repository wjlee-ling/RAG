import chromadb

from .templates import retrieval_prompt
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
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
print(vectorstore._collection.count())
retriever = vectorstore.as_retriever()
llm = ChatOpenAI(model_name="gpt-4-0125-preview", temperature=0, max_tokens=200)

retrieval_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | retrieval_prompt
    | llm
    | StrOutputParser()
)

resp = retrieval_chain.invoke("미궁365 보관방법은?")
print(resp)

## add chat messages

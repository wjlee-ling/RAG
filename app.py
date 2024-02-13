from backend.app.chains import build_pinecone_retrieval_chain
from backend.app.indexing import get_pinecone_vectorstore

import os
import sys
import wandb
import streamlit as st
from streamlit import session_state as sst
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_community.callbacks import wandb_tracing_enabled

__import__("pysqlite3")
if "pysqlite3" in sys.modules:
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

if "messages" not in sst:
    sst.messages = []


# os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
wandb.init(entity="wjlee-ling", project="sal-test")


@st.cache_resource
def get_pinecone_retrieval_chain(collection_name):
    print("☑️ Building a new pinecone retrieval chain...")
    pinecone_vectorstore = get_pinecone_vectorstore(collection_name)
    chain = build_pinecone_retrieval_chain(pinecone_vectorstore)
    return chain


st.title("RAG 데모")

# for message in sst.messages:
#     role = "human" if isinstance(message, HumanMessage) else "ai"

#     with st.chat_message(role):
#         st.markdown(message.content)

if prompt := st.chat_input("안녕하세요. 저는 Sales Bot입니다. 무엇을 도와드릴까요?"):
    sst.retrieval_chain = get_pinecone_retrieval_chain("test")

    # Display user message in chat message container
    with st.chat_message("human"):
        st.markdown(prompt)

    # Get assistant response
    with wandb_tracing_enabled():
        response = sst.retrieval_chain.invoke(prompt)
        print(response)
        retrieval_answer = response["answer"]
        retrieval_docs = response["context"]

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(retrieval_answer)

        with st.expander("정보 검색시 참고한 chunk"):
            tabs = st.tabs([f"doc{i}" for i in range(len(retrieval_docs))])
            for i in range(len(retrieval_docs)):
                tabs[i].write(retrieval_docs[i].page_content)
                tabs[i].write(retrieval_docs[i].metadata)
            # for doc in retrieval_docs:
            #     st.markdown(doc.page_content)

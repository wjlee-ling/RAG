from backend.app.chains import build_pinecone_retrieval_chain
from backend.app.indexing import get_pinecone_vectorstore
from backend.app.embeddings import KorRobertaEmbeddings

import os
import sys
import streamlit as st
from streamlit import session_state as sst

# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


if "messages" not in sst:
    sst.messages = []


@st.cache_resource
def get_pinecone_retrieval_chain(collection_name):
    print("☑️ Building a new pinecone retrieval chain...")
    pinecone_vectorstore = get_pinecone_vectorstore(
        index_name=collection_name,
        embedding_fn=KorRobertaEmbeddings(),
        dimension=768,
        namespace=None,
    )
    chain = build_pinecone_retrieval_chain(pinecone_vectorstore)
    return chain


st.title("RAG 데모")

# for message in sst.messages:
#     role = "human" if isinstance(message, HumanMessage) else "ai"

#     with st.chat_message(role):
#         st.markdown(message.content)

sst.retrieval_chain = get_pinecone_retrieval_chain("innocean")
if prompt := st.chat_input("정보 검색"):

    # Display user message in chat message container
    with st.chat_message("human"):
        st.markdown(prompt)

    # Get assistant response
    response = sst.retrieval_chain.invoke(prompt)

    retrieval_answer = response["final_answer"]
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

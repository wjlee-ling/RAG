from backend.app.chains import build_pinecone_retrieval_chain
from backend.app.indexing import get_pinecone_vectorstore
from backend.app.embeddings import KorRobertaEmbeddings
from backend.app.utils.aws import deploy_sagemaker_model

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


@st.cache_resource
def get_sagemaker_predictor(model_name):
    with st.spinner("🚀 Deploying sLLM to AWS Sagemaker..."):
        predictor = deploy_sagemaker_model(model_name)
    return predictor


st.title("RAG 데모")

# for message in sst.messages:
#     role = "human" if isinstance(message, HumanMessage) else "ai"

#     with st.chat_message(role):
#         st.markdown(message.content)

with st.spinner("환경 설정 중"):
    sst.retrieval_chain = get_pinecone_retrieval_chain(
        collection_name="innocean",
    )
    sst.predictor = get_sagemaker_predictor("mncai/mistral-7b-v5")

if prompt := st.chat_input("정보 검색"):

    # Display user message in chat message container
    with st.chat_message("human"):
        st.markdown(prompt)

    # Get assistant response
    final_inputs = sst.retrieval_chain.invoke(prompt)
    final_answer = sst.predictor.predict({"inputs": final_inputs["final_prompt"]})

    # retrieval_answer = response["final_answer"]
    retrieval_docs = final_inputs["context"]

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(final_answer)

        with st.expander("정보 검색시 참고한 chunk"):
            tabs = st.tabs([f"doc{i}" for i in range(len(retrieval_docs))])
            for i in range(len(retrieval_docs)):
                tabs[i].write(retrieval_docs[i].page_content)
                tabs[i].write(retrieval_docs[i].metadata)

from backend.app.chains import build_conversational_retrieval_chain, build_sales_chain

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
    sst.cp_messages = []
if "custom_retrieval_prompt_template" not in sst:
    sst.custom_retrieval_prompt_template = None
st.set_page_config(layout="wide")
# os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
wandb.init(entity="wjlee-ling", project="sal-test")


@st.cache_resource
def get_conversational_retrieval_chain(collection_name, retrieval_prompt_template):
    print("☑️ Building a new conversational retrieval chain...")
    conversational_retrieval_chain = build_conversational_retrieval_chain(
        collection_name, retrieval_prompt_template
    )
    return conversational_retrieval_chain


@st.cache_resource
def get_sales_chain(sales_prompt_template=None):
    print("☑️ Building a new sales chain...")
    return build_sales_chain(sales_prompt_template)


def reset():
    sst.messages = []
    if sst.custom_retrieval_prompt_template != sst.new_custom_retrieval_prompt_template:
        if (
            "{context}" not in sst.new_custom_retrieval_prompt_template
            and "{question}" not in sst.new_custom_retrieval_prompt_template
        ):
            st.error("{context} 와 {question}이 들어가 있는지 확인 필요합니다", icon="💥")

        sst.custom_retrieval_prompt_template = ChatPromptTemplate.from_template(
            sst.new_custom_retrieval_prompt_template
        )


st.title("SAL")
with st.expander("정보 검색 프롬프트 템플렛"):
    new_custom_retrieval_prompt_template = st.text_area(
        ":speech_balloon: 정보 검색 프롬프트:",
        placeholder="""[질문]에 [문맥]을 근거로만 답변하라:
[문맥] {context}

[질문] {question}
""",
        on_change=reset,
        key="new_custom_retrieval_prompt_template",
    )


for message in sst.messages:
    role = "human" if isinstance(message, HumanMessage) else "ai"

    with st.chat_message(role):
        st.markdown(message.content)

if prompt := st.chat_input("안녕하세요. 저는 Sales Bot입니다. 무엇을 도와드릴까요?"):
    sst.conversational_retrieval_chain = get_conversational_retrieval_chain(
        "test-0129", sst.custom_retrieval_prompt_template
    )
    sst.cp_conversational_retrieval_chain = get_conversational_retrieval_chain(
        "test-0131", sst.custom_retrieval_prompt_template
    )
    # sst.sales_chain = get_sales_chain()

    # Display user message in chat message container
    with st.chat_message("human"):
        st.markdown(prompt)
    # Add user message to chat history
    sst.messages.append(
        HumanMessage(content=prompt)
    )  # sst.messages.append({"role": "user", "content": prompt})

    sst.cp_messages.append(HumanMessage(content=prompt))  # 💥 cp.

    # Get assistant response
    print(sst.messages)
    with wandb_tracing_enabled():
        # step 1
        response = sst.conversational_retrieval_chain.invoke(
            {
                "question": prompt,
                "chat_history": sst.messages,
            }
        )
        retrieval_answer = response["answer"]
        retrieval_docs = response["docs"]

        # 💥 cp
        response_cp = sst.cp_conversational_retrieval_chain.invoke(
            {
                "question": prompt,
                "chat_history": sst.cp_messages,
            }
        )
        retrieval_answer_cp = response_cp["answer"]
        retrieval_docs_cp = response_cp["docs"]

        # # step 2
        # final_response = sst.sales_chain.invoke(
        #     {
        #         "question": HumanMessage(content=prompt),
        #         "context": retrieval_answer,
        #     }
        # )
        # print(final_response)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        col, col_cp = st.columns(2)
        with col:
            st.markdown(retrieval_answer.content)
            sst.messages.append(
                retrieval_answer  # AIMessage(content=answer)
            )  # sst.messages.append({"role": "assistant", "content": answer})

            # with st.expander("정보 검색 결과"):
            #     st.markdown(retrieval_answer)

            with st.expander("정보 검색시 참고한 chunk"):
                tabs = st.tabs([f"doc{i}" for i in range(len(retrieval_docs))])
                for i in range(len(retrieval_docs)):
                    tabs[i].write(retrieval_docs[i].page_content)
                    tabs[i].write(retrieval_docs[i].metadata)

        with col_cp:
            st.markdown(retrieval_answer_cp.content)  # 💥cp
            sst.messages.append(retrieval_answer_cp)  # 💥cp

            with st.expander("정보 검색시 참고한 chunk"):
                tabs = st.tabs([f"doc{i}" for i in range(len(retrieval_docs_cp))])
                for i in range(len(retrieval_docs_cp)):
                    tabs[i].write(retrieval_docs_cp[i].page_content)
                    tabs[i].write(retrieval_docs_cp[i].metadata)

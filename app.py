from backend.app.chains import build_conversational_retrieval_chain

import streamlit as st
from streamlit import session_state as sst
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

if "messages" not in sst:
    sst.messages = []
if "custom_retrieval_prompt_template" not in sst:
    sst.custom_retrieval_prompt_template = None
# if "bot_img" not in sst:
#     sst.bot_img = st.image(
#         "https://github.com/wjlee-ling/streamlit/assets/61496071/2c5836a3-666b-47bd-9165-36ab10de76bb"
#     )


@st.cache_resource
def get_conversational_retrieval_chain(retrieval_prompt_template):
    print("☑️ Building a new conversational retrieval chain...")
    conversational_retrieval_chain = build_conversational_retrieval_chain(
        retrieval_prompt_template
    )
    return conversational_retrieval_chain


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
        sst.custom_retrieval_prompt_template
    )

    # Display user message in chat message container
    with st.chat_message("human"):
        st.markdown(prompt)
    # Add user message to chat history
    sst.messages.append(
        HumanMessage(content=prompt)
    )  # sst.messages.append({"role": "user", "content": prompt})

    # Get assistant response
    print(sst.messages)
    response = sst.conversational_retrieval_chain.invoke(
        {
            "question": prompt,
            "chat_history": sst.messages,
        }
    )
    answer = response["answer"].content
    docs = response["docs"]
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(answer)
        sst.messages.append(
            AIMessage(content=answer)
        )  # sst.messages.append({"role": "assistant", "content": answer})

        with st.expander("정보 검색 결과"):
            for doc in docs:
                st.info(doc)

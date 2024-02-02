from backend.app.chains import (
    build_conversational_chain,
    build_sales_chain,
)
from backend.app.templates import TEST_0131_PROMPT

# import sys

# import wandb
import streamlit as st
from streamlit import session_state as sst
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_community.callbacks import wandb_tracing_enabled
from langchain_openai import ChatOpenAI

# __import__("pysqlite3")
# if "pysqlite3" in sys.modules:
#     sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")


@st.cache_resource
def get_llm(model_name="gpt-4-0125-preview", temp=0.0):
    print("☑️ Building a new llm...")
    return ChatOpenAI(model_name=model_name, temperature=temp, verbose=True)


@st.cache_resource
def get_conversational_chain(_llm):
    print("☑️ Building a new conversational  chain...")
    conversational_chain = build_conversational_chain(_llm)
    return conversational_chain


@st.cache_resource
def get_sales_chain(_sales_prompt_template=None):
    print("☑️ Building a new sales chain...")
    return build_sales_chain(_sales_prompt_template)


def recheck():
    sst.checked[-1][1] = not sst.checked[-1][1]
    print("updated!")


GREETING = "안녕하세요. 올리브영입니다. 찾으시는 제품이 있거나 도움이 필요하시면 말씀해 주세요."
GUIDELINE = """\
### 세일즈 봇이란?
제품 구매를 망설이는 고객에게 대화를 통해 가장 적합한 제품을 추천하고 구매를 유도한다.
                
### 평가목적
1. 고객의 입장에서 세일즈봇이 제품 구매를 얼마나 잘 유도하는지 평가한다. 
2. 세일즈봇이 고객의 니즈를 파악하여 필요한 제품을 얼마나 잘 추천하는지 평가한다.

### 방법
#### 대화
1. 역할
- 평가자: 고객
- 세일즈봇: 올리브영 영업 사원
2. 상황
- 평가자는 제품 구매를 고민하는 고객으로서 세일즈봇과 이와 관련한 상담을 진행한다.
3. 상세 규칙
- 고객이 문의하는 제품은 올리브영에서 판매하는 제품 중에서 자유롭게 선정 가능하다. (ex. 화장품, 영양제, 문구류 등)
- 단, 휴지, 물 등 생필품이 아닌 구매가 고민될 수 있는 제품으로 상담을 진행한다.
- 존대 혹은 반말 사용은 자유롭게 선택 가능하다.
- 최소 5턴~최대 10턴의 대화를 주고 받는다.
- 대화를 진행하는 과정에서 세일즈봇의 답변이 마음에 들지 않는 경우 체크를 클릭한다.
- 대화의 종결은 '제품 구매' 혹은 '구매 이탈'로 구분한다. 평가자는 세일즈봇과 대화 후 제품을 구매할지, 구매하지 않을지 결정하여 마지막 발화로 작성한다.
ex. 제품 구매 시, '그럼 그걸로 살게요' 등 / 구매 이탈 시, '다음에 살게요' 등 -> 표현에 제약은 없으며 자유롭게 작성한다.

#### 저장
세일즈봇과 대화를 종료한 후 TXT 파일을 다운

#### 설문지 참여
1. 대화 테스트 종료 후, 설문 조사에 참여한다.
2. 평가 일정 내 반드시 설문 조사까지 응하여야 본 테스트가 종료된다.
"""
LINK = (
    "https://docs.google.com/forms/d/1bI9DQyiwT3bm_Qr11c5lKWSs7gROTUDCPIkhjbIhNac/edit"
)


def display_link_msg():
    st.info(f"감사합니다! 이제 다음 링크에서 설문조사를 진행해주세요: {LINK}")


if "messages" not in sst:
    sst.messages = []  # [AIMessage(content=GREETING)]
    sst.condense_llm = get_llm("gpt-4-0125-preview")
    sst.conversational_chain = get_conversational_chain(sst.condense_llm)
    sst.sales_chain = get_sales_chain(TEST_0131_PROMPT)
    sst.checked = []
    sst.submit = False
    sst.user_name = ""

st.title("ㅌ넷 세일즈봇 대화 평가")
# with st.sidebar:
#     sst.user_name = st.text_input("필수: 닉네임을 입력해주세요. [:red 다섯 음절 이상]")

if sst.submit is False:
    with st.form("index"):
        sst.user_name = st.text_input("필수: **닉네임**을 입력해주세요.")
        sst.question1 = st.radio("질문 1. 현재 올리브영에서 사고 싶은 제품이 있습니까?", ["예", "아니요"])
        sst.question2 = st.select_slider(
            "질문 2. 사고 싶은 제품이 있으시다면 (질문 1에서 '예' 선택) 얼마나 사고 싶은지 점수로 얘기해주세요. (사고 싶은 마음이 클수록 높은 숫자)",
            options=range(1, 11),
        )
        if sst.question1 == "아니요":
            sst.question2 = 1

        st.markdown("## 가이드라인")
        st.markdown(GUIDELINE)
        sst.submit = st.form_submit_button("세일즈봇과 대화 시작")

else:
    with st.expander("가이드라인 다시 읽기", expanded=False):
        st.markdown(GUIDELINE)

    with st.chat_message("ai"):
        st.markdown(GREETING)
    for i, message in enumerate(sst.messages):
        role = "human" if isinstance(message, HumanMessage) else "ai"

        with st.chat_message(role):
            if role == "ai":
                if sst.checked[i][1] == True:
                    st.markdown(":red[" + message.content + "]")
                else:
                    st.markdown(message.content)
            else:
                st.markdown(message.content)

    if prompt := st.chat_input(""):
        # Display user message in chat message container
        with st.chat_message("human"):
            st.markdown(prompt)
            sst.checked.append(["유저: " + prompt, False])

        # Get assistant response
        print(sst.messages)
        # with wandb_tracing_enabled():
        # step 1
        condense_question = sst.conversational_chain.invoke(
            {
                "question": prompt,
                "chat_history": sst.messages,
            }
        )
        print(condense_question)
        # Add user message to chat history
        sst.messages.append(HumanMessage(content=prompt))

        # step 2
        final_response = sst.sales_chain.stream(
            {
                "question": condense_question,
            }
        )

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_resp = ""
            for resp in final_response:
                full_resp += resp.content
                message_placeholder.markdown(full_resp + "▌")
            col_answer, col_check = st.columns([4, 1])
            with col_answer:
                message_placeholder.markdown(full_resp)
            with col_check:
                st.checkbox(
                    value=False,
                    label=":red[체크]",
                    on_change=recheck,
                )
        sst.messages.append(
            AIMessage(content=full_resp)
        )  # sst.messages.append({"role": "assistant", "content": answer})
        sst.checked.append(["GPT: " + full_resp, False])

        if len(sst.messages) >= 10:
            btn = st.download_button(
                label="테스트 종료 및 txt 파일 저장",
                data="\n".join([msg + " --> " + str(ch) for (msg, ch) in sst.checked]),
                file_name=f"{sst.user_name}.txt",
                on_click=display_link_msg,
            )

from langchain_core.prompts import ChatPromptTemplate


retrieval_template = """[질문]에 [문맥]을 바탕으로만 답변하라:
[문맥] {context}

[질문] {question}
"""
retrieval_prompt = ChatPromptTemplate.from_template(retrieval_template)

# https://python.langchain.com/docs/expression_language/cookbook/retrieval

from langchain.schema import format_document
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate


def combine_docs(docs):
    """
    Combine retrieved docs into a single string w/ format_document(https://api.python.langchain.com/en/v0.0.339/schema/langchain.schema.prompt_template.format_document.html)
    """
    doc_prompt = PromptTemplate.from_template(template="{page_content}")
    doc_strings = [format_document(doc, doc_prompt) for doc in docs]
    return "\n\n".join(doc_strings)


retrieval_template = """[질문]에 [문맥]을 근거로만 답변하라:
[문맥] {context}

[질문] {question}
"""
retrieval_prompt = ChatPromptTemplate.from_template(retrieval_template)

## Conversational Retrieval Chain
condense_template = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question, in its original language.

Chat History:
{chat_history}
Follow Up Input: {question}
Standalone question:"""
condense_question_prompt = PromptTemplate.from_template(condense_template)

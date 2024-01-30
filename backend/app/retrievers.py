from .templates import SELF_QUERY_PROMPT
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import (
    AttributeInfo,
    StructuredQueryOutputParser,
    get_query_constructor_prompt,
)
from langchain.retrievers.self_query.chroma import ChromaTranslator
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings


def build_olive_selfquery_constructor(llm=None):
    metadata_field_olive_info = [
        AttributeInfo(
            name="category",
            description="category of the product. One of ['vitamin', 'Lactobacillus', 'slimming/innerbeauty']",
            type="string",
        ),
        AttributeInfo(
            name="price",
            description="original price of the product",
            type="integer",
        ),
        AttributeInfo(
            name="sale-price",
            description="Sale price of the product. If different from the original price, it is considered to be on sale",
            type="integer",
        ),
        AttributeInfo(
            name="name",
            description="Name of the product",
            type="string",
        ),
        AttributeInfo(
            name="brand",
            description="Brand of the product",
            type="string",
        ),
        AttributeInfo(
            name="rating",
            description="A 1-5 rating for the product review. 4-5 is excellent, 3-5 is positive, 1-2 is bad",
            type="float",
        ),
        # AttributeInfo(
        #     name="intent",
        #     description="Intent of the user query. One of ['recommend', 'search', 'exit', 'chitchat']",
        #     type="float",
        # ),
    ]
    document_content_description = "vitamin(비타민), Lactobacillus(유산균), slimming/innerbeauty(슬리밍/이너뷰티) 제품 **판매** 정보. The filters should be written in Korean"

    # break-down w/o retriever
    prompt = get_query_constructor_prompt(
        document_content_description, metadata_field_olive_info
    )
    output_parser = StructuredQueryOutputParser.from_components()
    query_constructor = prompt | llm | output_parser

    return query_constructor


def build_olive_retriever(query_constructor, vectorstore):
    retriever = SelfQueryRetriever(
        query_constructor=query_constructor,
        vectorstore=vectorstore,
        structured_query_translator=ChromaTranslator(),
    )
    return retriever


def get_query_response(query_constructor, retriever, query):
    response = query_constructor.invoke({"query": query})
    print(response, end="⭐⭐\n")
    return retriever.invoke(query)


query_ls = [
    "오쏘몰의 비타민 추천 좀",
    # "13000원 이하 고려은단의 비타민 검색",
    # "유산균 아무거나 추천",
    "후기 좋은 비타민 제품 보여줘",
]
llm = ChatOpenAI(temperature=0)
vectorstore = Chroma(
    persist_directory="backend/database/vectorstore/chroma",
    # client=persistent_client,
    collection_name="test-0131-eng",
    embedding_function=OpenAIEmbeddings(),
)
query_constructor = build_olive_selfquery_constructor(llm=llm)
retriever = build_olive_retriever(query_constructor, vectorstore=vectorstore)

for query in query_ls:
    print(query)
    resp = get_query_response(query_constructor, retriever, query)
    for item in resp:
        print(item)
    print("==========================")

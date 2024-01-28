from typing import Iterable

from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    MarkdownHeaderTextSplitter,
)
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings


def add_to_metadata(docs: Iterable[Document]) -> Iterable[Document]:
    """상품 판매정보 (가격, 상품명 등)를 메타데이터로 사용하기 위해 `DocumentLoader`로 로드된 doc의 메타데이터로 등록"""
    import re

    pattern = r"- (\w+): (.+)"
    mapping = {
        "prdDisplayName": "상품명",
        "prdBrand": "브랜드",
        "prdPrice": "정가",
        "prdSalePrice": "판매가",
        "prdCategroy": "분류",
    }

    for doc in docs:
        text_prd = re.search(
            r"(?<=## 판매 정보).+(?=## 상품정보 제공고시)", doc.page_content, re.DOTALL
        ).group()  # re.DOTALL setting for matching '.' with newlines as well
        matches = re.findall(pattern, text_prd)
        new_metadata = {}
        for match in matches:
            new_metadata[mapping[match[0]]] = match[1].strip(",'")
        doc.metadata.update(new_metadata)

    return docs


## loading and chunking
loader = DirectoryLoader(
    "../database/",
    glob="**/*.md.txt",
    loader_cls=TextLoader,
)
docs = loader.load()
docs = add_to_metadata(docs[:3])

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["#{2,5}", "\n---+\n+", "\n\n+"],
    keep_separator=True,
    is_separator_regex=True,
    add_start_index=True,
)

chunks = splitter.split_documents(docs)
# print(chunks)

## vectorization
vs = Chroma.from_documents(
    documents=chunks,
    embedding=OpenAIEmbeddings(),
    persist_directory="../database/vectorstore/chroma",
    collection_name="test",
    collection_metadata={
        "hnsw:space": "cosine",
    },
)
# collection = vs._collection  ## the collection "test"

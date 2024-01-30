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
        "prdDisplayName": "name",  # "상품명",
        "prdBrand": "brand",  # "브랜드",
        "prdPrice": "price",  # "정가",
        "prdSalePrice": "sale-price",  # "판매가",
        "prdCategory": "category",  # "분류",
    }

    for doc in docs:
        text_prd = re.search(
            r"(?<=## 판매 정보).+(?=## 상품정보 제공고시)", doc.page_content, re.DOTALL
        ).group()  # re.DOTALL setting for matching '.' with newlines as well
        matches = re.findall(pattern, text_prd)
        new_metadata = {}
        for match in matches:
            if match[0] in ["prdPrice", "prdSalePrice"]:
                try:
                    new_metadata[mapping[match[0]]] = int(
                        match[1].strip("원,'~ ").replace(",", "")
                    )
                except:
                    new_metadata[mapping["prdPrice"]] = None
            else:
                new_metadata[mapping[match[0]]] = match[1].strip(",' ")
        if new_metadata[mapping["prdPrice"]] is None:  #  no sale
            new_metadata[mapping["prdPrice"]] = new_metadata[mapping["prdSalePrice"]]
        doc.metadata.update(new_metadata)
    return docs


def append_metadata_to_data(docs: Iterable[Document]) -> Iterable[Document]:
    """chunk에 메타데이터로 들어가 있는 제품정보 추가"""
    import json

    for doc in docs:
        if "## 판매 정보" not in doc.page_content:
            metadata_str = json.dumps(doc.metadata, ensure_ascii=False)
            doc.page_content = (
                "## 판매 정보\n" + metadata_str + "\n---\n\n" + doc.page_content
            )
    return docs


## loading and chunking
loader = DirectoryLoader(
    "backend/database/raw/0128/",
    glob="**/*.md.txt",
    loader_cls=TextLoader,
)
docs = loader.load()
docs = add_to_metadata(docs)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=5000,  # 5000 for gpt-4-0125-preview: 128,000 tokens
    chunk_overlap=150,
    separators=["#{2,5}", "\n---+\n+", "\n\n+"],
    keep_separator=True,
    is_separator_regex=True,
    add_start_index=True,
)

chunks = splitter.split_documents(docs)
chunks = append_metadata_to_data(chunks)
# print(chunks)

# vectorization
vs = Chroma.from_documents(
    documents=chunks,
    embedding=OpenAIEmbeddings(),
    persist_directory="backend/database/vectorstore/chroma",
    ids=[str(i) for i in range(1, len(chunks) + 1)],
    collection_name="test-0131-eng",
    collection_metadata={
        "hnsw:space": "cosine",
    },
)
print(f"💥New collection made w/ {vs._collection.count()} document(s).")

## to use
# persistent_client = chromadb.PersistentClient()
# collection = persistent_client.get_or_create_collection("collection_name")

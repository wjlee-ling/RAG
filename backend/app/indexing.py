import os

from typing import Iterable, List
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    MarkdownHeaderTextSplitter,
)
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings


load_dotenv()
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")


def create_or_get_pinecone_index(index_name: str, dimension: int = 1536):
    from pinecone import Pinecone, ServerlessSpec

    client = Pinecone(api_key=PINECONE_API_KEY)
    if index_name in [index["name"] for index in client.list_indexes()]:
        pc_index = client.Index(index_name)
        print("☑️ Got the existing Pinecone index")
    else:
        client.create_index(
            name=index_name,
            dimension=dimension,
            metric="cosine",
            spec=ServerlessSpec("aws", "us-west-2"),
        )
        pc_index = client.Index(index_name)
        print("☑️ Created a new Pinecone index")

    print(pc_index.describe_index_stats())
    return pc_index


def get_pinecone_vectorstore(
    index_name: str,
    embedding_fn=OpenAIEmbeddings(),
    dimension: int = 1536,
    namespace: str = None,
):
    from langchain_pinecone import Pinecone

    index = create_or_get_pinecone_index(
        index_name,
        dimension,
    )

    vs = Pinecone(
        index,
        embedding_fn,
        pinecone_api_key=PINECONE_API_KEY,
        index_name=index_name,
        namespace=namespace,
    )

    return vs


def upsert_docs_to_pinecone(
    index_name, embedding_fn, docs: List[Document], namespace: str = None
):
    from langchain_pinecone import Pinecone

    texts, metadatas, ids = [], [], []
    for doc in docs:
        ids.append(doc.metadata.pop("id", None))
        texts.append(doc.page_content)
        metadatas.append(doc.metadata)

    if ids[0] is None:
        ids = None

    ids = Pinecone.from_texts(
        texts=texts,
        embedding=embedding_fn,
        metadatas=metadatas,
        ids=ids,
        index_name=index_name,
        namespace=namespace,
        embedding_chunk_size=1000,  # set to a high number
        show_progress=True,
    )
    counts = len(ids)
    print(f"💥Upserted {str(counts)} new document(s) to Pinecone.")


def create_chromadb_index():
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

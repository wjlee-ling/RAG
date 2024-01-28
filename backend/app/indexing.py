from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    MarkdownHeaderTextSplitter,
)
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

## loading and chunking
loader = DirectoryLoader(
    "../database/",
    glob="**/*.md.txt",
    loader_cls=TextLoader,
)
docs = loader.load()

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

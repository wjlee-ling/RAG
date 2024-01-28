from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    MarkdownHeaderTextSplitter,
)


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
)

# chunks = splitter.split_documents([docs[0]])

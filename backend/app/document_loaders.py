from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import MarkdownTextSplitter


loader = DirectoryLoader(
    "../database/",
    glob="**/*.md.txt",
    loader_cls=TextLoader,
)
docs = loader.load()

splitter = MarkdownTextSplitter(chunk_size=500, chunk_overlap=50, separator="##")
chunks = splitter.split_documents([docs[0]])
for chunk in chunks:
    print(chunk)

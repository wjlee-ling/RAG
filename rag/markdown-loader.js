import { TextLoader } from "langchain/document_loaders/fs/text";

const loader = new TextLoader("마크다운.md");
const docs = await loader.load();
console.log({ docs });

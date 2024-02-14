from typing import List, Dict

from langchain_core.documents import Document


def load_docs_from_csv(
    file_path: str,
    content_cols: List[str],
    metadata_mapping: Dict[str, str],
) -> List[Document]:

    import csv

    def __read_file(csv_file):
        docs = []

        csv_reader = csv.DictReader(csv_file)
        for i, row in enumerate(csv_reader):
            content = "\n".join([row[col] for col in content_cols]).strip()

            metadata = {"row": str(i)}
            for old_name, new_name in metadata_mapping.items():
                metadata[new_name] = row[old_name]

            doc = Document(page_content=content, metadata=metadata)
            docs.append(doc)
        return docs

    with open(file_path, newline="", encoding="utf-8") as csv_file:
        docs = __read_file(csv_file)

    return docs


# metadata_mapping = {
#     "출처 페이지": "page",
#     "출처 열": "source_passage",
#     "A": "answer",
# }
# docs = load_docs_from_csv(
#     file_path="/Users/lwj/workspace/RAG/backend/database/이노션 QA셋 - Sheet1.csv",
#     content_cols=["Q"],
#     metadata_mapping=metadata_mapping,
# )

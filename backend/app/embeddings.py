from typing import List

from langchain_core.embeddings import Embeddings
from transformers import AutoModel, AutoTokenizer


def get_roberta_embeddings(sentences: List[str]):
    """
    Get features of Korean input texts w/ BM-K/KoSimCSE-roberta.
    Returns:
        List[List[int]] of dimension 768
    """
    model = AutoModel.from_pretrained("BM-K/KoSimCSE-roberta")
    tokenizer = AutoTokenizer.from_pretrained("BM-K/KoSimCSE-roberta")
    inputs = tokenizer(sentences, padding=True, truncation=True, return_tensors="pt")
    embeddings, _ = model(**inputs, return_dict=False)
    ls = []
    for embedding in embeddings:
        vector = embedding[0].detach().numpy().tolist()
        ls.append(vector)
    return ls


class KorRobertaEmbeddings(Embeddings):
    """Feature Extraction w/ BM-K/KoSimCSE-roberta"""

    dimension = 768

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return get_roberta_embeddings(texts)

    def embed_query(self, text: str) -> List[float]:
        return get_roberta_embeddings([text])[0]

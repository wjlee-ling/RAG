from typing import List
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

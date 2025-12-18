# main.py
# TD6 : construction du corpus à partir des APIs
# TD7 : ajout du moteur de recherche (SearchEngine)

import pandas as pd
from Corpus import Corpus
from SearchEngine import SearchEngine
from apis import *


def build_corpus(keyword):

    reddit_docs = fetch_reddit(keyword)      # Fetch Reddit docs
    arxiv_docs = fetch_arxiv(keyword)        # Fetch arXiv docs

    all_docs = reddit_docs + arxiv_docs

    for i, d in enumerate(all_docs):
        d["id"] = i  # simple numeric ID

    df = pd.DataFrame(all_docs, columns=[
        "id", "titre", "auteur", "date", "url", "texte", "type", "extra"
    ])
    
    df.to_csv("corpus.csv", sep="\t", index=False)
    print("\nAPI Corpus saved in corpus.csv\n")


if __name__ == "__main__":
    
    build_corpus("computer")   # à lancer une fois si besoin

    corpus = Corpus("API Corpus")
    corpus.load("corpus.csv")

    # TD6 : exemples 
    corpus.show_by_date()
    print(corpus.search("computer"))
    print(corpus.concorde("computer"))
    corpus.stats(10)

    # TD7 : moteur de recherche
    print("\n---- SearchEngine / TD7 ----\n")
    engine = SearchEngine(corpus)

    # test
    df_res = engine.search("computer", k=5)
    print(df_res)   
# main.py
# Main script: builds a corpus from external APIs, saves it to a CSV file,
# then loads it into a Corpus object and displays the documents by date.

import pandas as pd
from Corpus import Corpus
from apis import *


def build_corpus(keyword):

    reddit_docs = fetch_reddit(keyword)      # Fetch Reddit docs
    arxiv_docs = fetch_arxiv(keyword)  # Fetch arXiv docs

    all_docs = reddit_docs + arxiv_docs  # Merge both sources

    for i, d in enumerate(all_docs):
        d["id"] = i  # Add simple numeric ID

    df = pd.DataFrame(all_docs, columns=[
        "id", "titre", "auteur", "date", "url", "texte", "type", "extra"
    ])
    
    df.to_csv("corpus.csv", sep=";", index=False)  # Save CSV file

    print("\nAPI Corpus saved in corpus.csv\n")


if __name__ == "__main__":
    
    build_corpus("python")  # Build corpus from keyword
    
    
    corpus = Corpus("API Corpus")
    corpus.load("corpus.csv")  # Load saved CSV


    print("\n---- Sorted by date -------\n")
    corpus.show_by_date()      # Show documents by date

    
    print("\n---- Recherche A Word -------\n")
    print(corpus.search("Python"))


    print("\n---- Corcorder The Words -------\n")
    print(corpus.concorde("Python"))
    
     
    print("\n---- Top 10 Words in Corpus -------\n")
    corpus.stats(10)

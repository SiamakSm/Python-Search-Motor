# Corpus.py
# Corpus class (singleton) that stores all documents and authors.
# It handles: creating a unique shared corpus instance, adding documents,
# tracking authors, loading documents from a CSV file, and displaying
# documents sorted by date.

import pandas as pd
import datetime
from Author import Author
from Factory import factoryClass


class Corpus:
    _instance = None

    def __new__(cls, nom):
        # Ensure only one Corpus instance exists (singleton)
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, nom):
        # Initialize attributes only once
        if not hasattr(self, "initialized"):
            self.nom = nom
            self.id2doc = {}     # id → document
            self.authors = {}    # author name → Author object
            self.ndoc = 0        # number of documents
            self.naut = 0        # number of authors (not used)
            self.initialized = True

    def add_document(self, doc):
        # Store document with an incremental ID
        doc_id = self.ndoc
        self.id2doc[doc_id] = doc
        self.ndoc += 1

        # Register author if not already present, then attach document
        aut = doc.auteur
        if aut not in self.authors:
            self.authors[aut] = Author(aut)
        self.authors[aut].add(doc_id, doc)

    def load(self, chemin="corpus.csv"):
        # Load documents from a CSV and reconstruct objects via factoryClass
        df = pd.read_csv(chemin, sep=";")

        for _, row in df.iterrows():
            # Convert date string into datetime
            date_obj = datetime.datetime.strptime(row["date"], "%Y-%m-%d")

            # Create correct document type depending on source
            if row["type"].lower() == "reddit":
                doc = factoryClass.create(
                    "reddit",
                    row["titre"],
                    row["auteur"],
                    date_obj,
                    row["url"],
                    row["texte"],
                    int(row["extra"])     # number of comments
                )

            elif row["type"].lower() == "arxiv":
                # extra column contains all authors concatenated
                authors = str(row["extra"]).split("|")
                authors = [a.strip() for a in authors if a.strip()]
                doc = factoryClass.create(
                    "arxiv",
                    row["titre"],
                    authors,              # list of authors
                    date_obj,
                    row["url"],
                    row["texte"]
                )

            # Add reconstructed document to corpus
            self.add_document(doc)

        print("\nCorpus loaded from", chemin)

    def show_by_date(self):
        # Display all documents sorted by their date attribute
        docs = sorted(self.id2doc.values(), key=lambda d: d.date)
        for d in docs:
            print(f"[{d.getType()}] {d}")
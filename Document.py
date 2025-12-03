# Document.py
# Base Document class and its two subclasses.
# This module defines: a generic document structure, a Reddit-specific
# document (with comment count), and an arXiv document (with multiple authors).

class Document:
    def __init__(self, titre, auteur, date, url, texte):
        # Basic attributes shared by all documents
        self.titre = titre
        self.auteur = auteur
        self.date = date
        self.url = url
        self.texte = texte
        self.type = "generic"   # default type

    def getType(self):
        # Return document type (overwritten in subclasses)
        return self.type

    def __str__(self):
        # Default string representation
        return f"{self.titre} ({self.auteur}, {self.date})"


class RedditDocument(Document):
    def __init__(self, titre, auteur, date, url, texte, nbComments):
        # Inherit all base attributes
        super().__init__(titre, auteur, date, url, texte)
        self.nbComments = nbComments     # number of comments
        self.type = "Reddit"

    def __str__(self):
        # Custom display for Reddit documents
        return f"Reddit : {self.titre} ({self.nbComments} commentaires)"


class ArxivDocument(Document):
    def __init__(self, titre, auteurs, date, url, texte):
        # Use first author as main author for the base class
        super().__init__(titre, auteurs[0], date, url, texte)
        self.coAuteurs = auteurs         # list of all authors
        self.type = "Arxiv"

    def __str__(self):
        # Custom display for arXiv documents
        return f"Arxiv : {self.titre} ({len(self.coAuteurs)} auteurs)"
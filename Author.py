# Author.py
# Author class that stores an author's name and all documents written by them.
# It keeps track of how many documents the author has and provides a simple
# interface to register new documents.

class Author:
    def __init__(self, name):
        # Basic attributes for tracking an author's production
        self.name = name
        self.ndoc = 0                # number of documents
        self.production = {}         # id_doc → Document object

    def add(self, id_doc, document):
        # Register a new document for the author
        self.production[id_doc] = document
        self.ndoc = len(self.production)  # update count

    def __str__(self):
        # String representation showing name + number of documents
        return f"{self.name} ({self.ndoc} documents)"
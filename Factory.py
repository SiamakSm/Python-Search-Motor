# Factory.py
# Simple factory class used to create the correct type of Document object
# (RedditDocument or ArxivDocument) based on a string identifier.

from Document import RedditDocument, ArxivDocument


class factoryClass:

    @staticmethod
    def create(doc_type, *args, **kwargs):
        # Select the appropriate document subclass to instantiate

        if doc_type.lower() == "reddit":
            return RedditDocument(*args, **kwargs)

        elif doc_type.lower() == "arxiv":
            return ArxivDocument(*args, **kwargs)

        else:
            # If the type does not match any known document type
            raise ValueError(f"Unknown document type: {doc_type}")
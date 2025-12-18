# Corpus.py
# Corpus class (singleton) that stores all documents and authors.
# TD6 : chargement / stats / recherche simple
# TD7 : ajout du vocabulaire pour moteur de recherche (SearchEngine)

import pandas as pd
import datetime
import re
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
            #self.naut = 0        # number of authors (not used)
            self.initialized = True
            self.allText = None
            
            
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
        df = pd.read_csv(chemin, sep="\t")

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
            
    
    def get_all_text(self):
        if self.allText is None:
            self.allText = "\n".join(str(doc.texte) for doc in self.id2doc.values())
        return self.allText
    
           
    def search(self, keysword):
        # TD6 : petite recherche textuelle globale
        allText = self.get_all_text()
        pattern = re.compile(re.escape(keysword), re.IGNORECASE)
        results = []

        for match in pattern.finditer(allText):
            start_index = max(0, match.start() - 10)
            end_index = min(len(allText), match.end() + 10)

            snippet = allText[start_index:end_index].replace('\n', ' ')
            results.append(f"...{snippet}...")            
        return results
    
    
    def concorde(self, keysword, size=10):
        allText = self.get_all_text()
        pattern = re.compile(re.escape(keysword), re.IGNORECASE)
        data = []

        for match in pattern.finditer(allText):
            start_index = max(0, match.start() - size)
            end_index = min(len(allText), match.end() + size)

            leftContext = allText[start_index:match.start()]
            rightContext = allText[match.end():end_index]
            snippet = allText[match.start():match.end()].replace('\n', ' ')

            data.append([f"...{leftContext} ", f"    {snippet}   ", f"       {rightContext}...."])
            df = pd.DataFrame(data, columns=["Context de gauche", "motif trouvé", "Context de droite" ])            
        return df
    
    
    # ---------- TD7 : nettoyage utilisé par stats + moteur de recherche ----------
    def nettoyer_texte(self, texte):
        texte = texte.lower()
        texte = texte.replace('\n', ' ')
        texte = re.sub(r'[0-9]+', ' ', texte)
        texte = re.sub(r'[^a-zàâäçéèêëîïôöùûüÿñæœ\s]', ' ', texte)
        texte = re.sub(r'\s+', ' ', texte).strip()
        return texte
    
    
    def stats(self, n_top=10):
        vocabulaire = set() # Pour éliminer les doublons
        mots_comptes = {}   # Pour stocker le nombre d'occurrences (Term Frequency)
        doc_compte = {}     # Pour stocker le nombre de documents (Document Frequency)
        
        for doc in self.id2doc.values():
            texte_nettoye = self.nettoyer_texte(str(doc.texte))
            mots = texte_nettoye.split()
            
            doc_vocab = set(mots)
            vocabulaire.update(doc_vocab)
            
            for mot in mots:
                if mot in mots_comptes:
                    mots_comptes[mot] += 1
                else:
                    mots_comptes[mot] = 1

            for mot in doc_vocab:
                if mot in doc_compte:
                    doc_compte[mot] += 1
                else:
                    doc_compte[mot] = 1

        print(f"--- Statistiques du Corpus '{self.nom}' ---")
        print(f"Nombre de mots différents (Taille du vocabulaire) : {len(vocabulaire)}")
        
        freq_series = pd.Series(mots_comptes)
        df_freq = pd.DataFrame(freq_series, columns=['Term Frequency (TF)'])
        df_freq.index.name = 'Mot'
        
        df_freq['Document Frequency (DF)'] = pd.Series(doc_compte)
        df_top_n = df_freq.sort_values(by='Term Frequency (TF)', ascending=False).head(n_top)
        
        print(f"\n--- {n_top} mots les plus fréquents ---")
        print(df_top_n)
        
        return df_freq

    
    # ---------- TD7 : vocabulaire (Partie 1.1) ----------
    def vocab(self):
        vocab = {}
        index = 0

        for doc in self.id2doc.values():
            texte = self.nettoyer_texte(str(doc.texte))
            for mot in texte.split():
                if mot not in vocab:
                    vocab[mot] = {"id": index, "total_occ": 0, "doc_occ": 0}
                    index += 1

        print("Nombre de mots du vocabulaire :", len(vocab))
        return vocab
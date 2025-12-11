# SearchEngine.py
# TD7 : moteur de recherche basé sur TF, IDF, TF-IDF et similarité cosinus

from collections import Counter
import math
import pandas as pd


class SearchEngine:

    def __init__(self, corpus):
        self.corpus = corpus
        self.vocab = corpus.vocab()    # Partie 1.1 TD7

        self.mat_TF = None
        self.idf = None
        self.mat_TFxIDF = None

        # Partie 1.2 + 1.3
        self.build_TF_matrix()

        # Partie 1.4
        self.build_IDF()
        self.build_TF_IDF_matrix()


    # ---------------------- PARTIE 1.2 + 1.3 : TF ----------------------
    def build_TF_matrix(self):
        nb_docs = self.corpus.ndoc
        nb_mots = len(self.vocab)

        # matrice TF : docs × mots
        self.mat_TF = [[0 for _ in range(nb_mots)] for _ in range(nb_docs)]

        id_mot = {mot: info["id"] for mot, info in self.vocab.items()}

        total_occ = [0] * nb_mots
        doc_occ = [0] * nb_mots

        for doc_id, doc in self.corpus.id2doc.items():
            texte = self.corpus.nettoyer_texte(str(doc.texte))
            mots = texte.split()

            freq = Counter(mots)
            uniques = set(mots)

            for mot, c in freq.items():
                j = id_mot[mot]
                self.mat_TF[doc_id][j] = c
                total_occ[j] += c

            for mot in uniques:
                j = id_mot[mot]
                doc_occ[j] += 1

        # mettre à jour vocab
        for mot, info in self.vocab.items():
            j = info["id"]
            info["total_occ"] = total_occ[j]
            info["doc_occ"] = doc_occ[j]

        print("Matrice TF construite.")


    # ---------------------- PARTIE 1.4 : IDF ---------------------------
    def build_IDF(self):
        N = self.corpus.ndoc
        nb_mots = len(self.vocab)

        self.idf = [0.0] * nb_mots

        for mot, info in self.vocab.items():
            j = info["id"]
            df = info["doc_occ"]
            if df > 0:
                self.idf[j] = math.log(N / df)
            else:
                self.idf[j] = 0.0

        print("IDF calculé.")


    # ----------------- PARTIE 1.4 : matrice TF-IDF ---------------------
    def build_TF_IDF_matrix(self):
        nb_docs = self.corpus.ndoc
        nb_mots = len(self.vocab)

        self.mat_TFxIDF = [[0.0 for _ in range(nb_mots)] for _ in range(nb_docs)]

        for i in range(nb_docs):
            for j in range(nb_mots):
                tf = self.mat_TF[i][j]
                if tf != 0:
                    self.mat_TFxIDF[i][j] = tf * self.idf[j]

        print("Matrice TF-IDF construite.")


    # ----------------- Vecteur de requête TF-IDF -----------------------
    def build_query_vector(self, query):
        nb_mots = len(self.vocab)
        q_vec = [0.0] * nb_mots

        texte = self.corpus.nettoyer_texte(str(query))
        mots = texte.split()

        freq = Counter(mots)

        for mot, c in freq.items():
            if mot in self.vocab:
                j = self.vocab[mot]["id"]
                q_vec[j] = c * self.idf[j]

        return q_vec


    # ----------------- Similarité cosinus ------------------------------
    def cosine(self, A, B):
        num = sum(a*b for a, b in zip(A, B))
        normA = math.sqrt(sum(a*a for a in A))
        normB = math.sqrt(sum(b*b for b in B))
        if normA == 0 or normB == 0:
            return 0.0
        return num / (normA * normB)


    # ----------------- Fonction search (Partie 2 + 3) ------------------
    def search(self, query, k=5):
        """
        Retourne un DataFrame avec les k documents les plus pertinents :
        colonnes : doc_id, titre, auteur, date, url, score
        """
        q_vec = self.build_query_vector(query)

        scores = []
        for doc_id in range(self.corpus.ndoc):
            d_vec = self.mat_TFxIDF[doc_id]
            s = self.cosine(q_vec, d_vec)
            scores.append((doc_id, s))

        scores = sorted(scores, key=lambda x: x[1], reverse=True)
        scores = [s for s in scores if s[1] > 0]
        top = scores[:k]

        rows = []
        for doc_id, score in top:
            doc = self.corpus.id2doc[doc_id]
            rows.append({
                "doc_id": doc_id,
                "titre": doc.titre,
                "auteur": doc.auteur,
                "date": doc.date,
                "url": doc.url,
                "score": score
            })

        return pd.DataFrame(rows)
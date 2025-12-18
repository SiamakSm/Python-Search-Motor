import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from collections import Counter
import re

# Import de vos classes
from Corpus import Corpus
from SearchEngine import SearchEngine

class AdvancedSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Moteur de Recherche & Analyseur de Corpus")
        self.root.geometry("1200x800")

        # Données
        self.corpus = None
        self.engine = None
        self.current_results = [] # Stocke les résultats de la recherche actuelle

        # --- Zone Supérieure : Contrôles ---
        self.top_frame = tk.Frame(root, bg="#f0f0f0", pady=10, padx=10)
        self.top_frame.pack(fill=tk.X)

        self.btn_load = tk.Button(self.top_frame, text="Charger Corpus", command=self.load_corpus, bg="#ddd")
        self.btn_load.pack(side=tk.LEFT, padx=5)

        tk.Label(self.top_frame, text="Recherche :", bg="#f0f0f0").pack(side=tk.LEFT, padx=5)
        self.entry_query = tk.Entry(self.top_frame, width=40)
        self.entry_query.pack(side=tk.LEFT, padx=5)

        tk.Label(self.top_frame, text="Nbr résultats :", bg="#f0f0f0").pack(side=tk.LEFT, padx=5)
        self.spin_k = tk.Spinbox(self.top_frame, from_=5, to=100, width=5)
        self.spin_k.pack(side=tk.LEFT)

        self.btn_search = tk.Button(self.top_frame, text="Rechercher", command=self.run_search, bg="lightblue")
        self.btn_search.pack(side=tk.LEFT, padx=10)

        # --- Zone Principale : Onglets ---
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # Création des onglets
        self.tab_results = tk.Frame(self.notebook)
        self.tab_doc_details = tk.Frame(self.notebook)
        self.tab_comparison = tk.Frame(self.notebook)

        self.notebook.add(self.tab_results, text="Résultats de Recherche")
        self.notebook.add(self.tab_doc_details, text="Détails du Document")
        self.notebook.add(self.tab_comparison, text="Comparaison")

        # Initialisation des contenus des onglets
        self.init_tab_results()
        self.init_tab_doc_details()
        self.init_tab_comparison()

    # -------------------------------------------------------------------------
    # UI SETUP
    # -------------------------------------------------------------------------
    def init_tab_results(self):
        # Tableau (Treeview) pour afficher les résultats
        columns = ("score", "type", "titre", "auteur", "date")
        self.tree = ttk.Treeview(self.tab_results, columns=columns, show='headings')
        
        self.tree.heading("score", text="Pertinence")
        self.tree.heading("type", text="Source")
        self.tree.heading("titre", text="Titre")
        self.tree.heading("auteur", text="Auteur")
        self.tree.heading("date", text="Date")

        self.tree.column("score", width=80)
        self.tree.column("type", width=80)
        self.tree.column("titre", width=400)
        self.tree.column("auteur", width=150)
        self.tree.column("date", width=100)

        self.tree.pack(expand=True, fill='both')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.tab_results, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Événement de sélection
        self.tree.bind("<<TreeviewSelect>>", self.on_document_select)

    def init_tab_doc_details(self):
        # Layout : Gauche 
        paned = tk.PanedWindow(self.tab_doc_details, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Gauche : Info textuelles
        self.frame_doc_info = tk.Frame(paned, padx=10, pady=10, bg="white")
        paned.add(self.frame_doc_info)

        self.lbl_doc_title = tk.Label(self.frame_doc_info, text="Sélectionnez un document...", font=("Arial", 14, "bold"), bg="white", wraplength=400)
        self.lbl_doc_title.pack(anchor="w")

        self.txt_content = tk.Text(self.frame_doc_info, height=20, width=50, wrap=tk.WORD)
        self.txt_content.pack(fill=tk.BOTH, expand=True, pady=10)

        # Droite : Graphe des mots fréquents
        self.frame_doc_graph = tk.Frame(paned, bg="#f9f9f9")
        paned.add(self.frame_doc_graph)

    def init_tab_comparison(self):
        # Conteneur pour les graphes comparatifs
        self.frame_comp_graphs = tk.Frame(self.tab_comparison)
        self.frame_comp_graphs.pack(fill=tk.BOTH, expand=True)


    def load_corpus(self):
        path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not path: return
        
        try:
            # Rechargement propre
            if Corpus._instance: Corpus._instance = None
            
            self.corpus = Corpus("App Corpus")
            self.corpus.load(path)
            
            # Init moteur de recherche
            self.engine = SearchEngine(self.corpus)
            
            messagebox.showinfo("Succès", f"Corpus chargé : {self.corpus.ndoc} documents.\nMoteur indexé.")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def run_search(self):
        if not self.engine:
            messagebox.showwarning("Attention", "Chargez d'abord un corpus.")
            return

        query = self.entry_query.get()
        k = int(self.spin_k.get())

        # Nettoyer l'interface
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        # Appel au moteur
        df_res = self.engine.search(query, k=k)
        
        # Stockage des résultats en mémoire
        self.current_results = [] # Reset

        if df_res.empty:
            messagebox.showinfo("Info", "Aucun résultat trouvé.")
            return

        # Remplissage du tableau
        for _, row in df_res.iterrows():
            doc_id = row['doc_id']
            score = f"{row['score']:.4f}"
            
            # Récupération de l'objet Document réel
            doc_obj = self.corpus.id2doc[doc_id]
            doc_type = doc_obj.getType()
            
            self.current_results.append(doc_obj) 

            # Insertion dans Treeview 
            self.tree.insert("", "end", iid=doc_id, values=(score, doc_type, row['titre'], row['auteur'], row['date']))

        # Mise à jour immédiate de l'onglet comparaison
        self.update_comparison_charts()
        
        # Focus sur l'onglet résultats
        self.notebook.select(self.tab_results)

    def on_document_select(self, event):
        # Quand on clique sur une ligne du tableau
        selected_item = self.tree.selection()
        if not selected_item: return

        doc_id = int(selected_item[0]) # L'ID a été stocké comme iid du treeview
        doc = self.corpus.id2doc[doc_id]

        # 1. Mise à jour infos texte
        self.lbl_doc_title.config(text=f"[{doc.getType()}] {doc.titre}")
        self.txt_content.delete("1.0", tk.END)
        self.txt_content.insert(tk.END, str(doc.texte))

        # 2. Calcul des Top Mots pour CE document
        text_clean = self.corpus.nettoyer_texte(str(doc.texte))
        words = text_clean.split()
        counter = Counter(words)
        common = counter.most_common(10)

        # 3. Dessiner le graphe
        self.draw_doc_stats(common)
        


    def draw_doc_stats(self, common_words):
        # Nettoyer le frame graphique
        for widget in self.frame_doc_graph.winfo_children():
            widget.destroy()

        if not common_words: return

        words, counts = zip(*common_words)

        fig, ax = plt.subplots(figsize=(5, 4))
        ax.barh(words, counts, color='skyblue')
        ax.set_title("Top 10 mots fréquents")
        ax.invert_yaxis() # Mots les plus fréquents en haut

        canvas = FigureCanvasTkAgg(fig, master=self.frame_doc_graph)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update_comparison_charts(self):
        # Nettoyer
        for widget in self.frame_comp_graphs.winfo_children():
            widget.destroy()

        if not self.current_results:
            tk.Label(self.frame_comp_graphs, text="Faites une recherche pour voir la comparaison.").pack(pady=20)
            return

        # Séparation
        reddit_docs = [d for d in self.current_results if "reddit" in d.getType().lower()]
        arxiv_docs = [d for d in self.current_results if "arxiv" in d.getType().lower()]

        # Configuration Matplotlib
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
        fig.suptitle(f"Comparaison sur les {len(self.current_results)} résultats trouvés", fontsize=14)

        # Graphe 1 : Camembert Répartition
        labels = ['Reddit', 'Arxiv']
        sizes = [len(reddit_docs), len(arxiv_docs)]
        colors = ['#ff4500', '#1b3e86'] # Couleurs officielles (à peu près)
        
        # Gestion du cas vide
        if sum(sizes) > 0:
            ax1.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
            ax1.set_title("Répartition des sources")
        else:
            ax1.text(0.5, 0.5, "Pas de données", ha='center')

        # Graphe 2 : Moyenne de longueur des textes (Comparaison de contenu)
        r_len = sum([len(str(d.texte)) for d in reddit_docs]) / len(reddit_docs) if reddit_docs else 0
        a_len = sum([len(str(d.texte)) for d in arxiv_docs]) / len(arxiv_docs) if arxiv_docs else 0
        
        ax2.bar(['Reddit', 'Arxiv'], [r_len, a_len], color=colors)
        ax2.set_title("Longueur moyenne des textes")

        # Affichage
        canvas = FigureCanvasTkAgg(fig, master=self.frame_comp_graphs)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Lancement
if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedSearchApp(root)
    root.mainloop()
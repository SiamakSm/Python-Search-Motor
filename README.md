
Python Search Motor – v1 (TD3 → TD5)

This first version builds a small corpus from Reddit and arXiv, saves it to a CSV file, then reloads it into Python objects and prints the documents ordered by date.

Project structure

Author.py        # Author objects

Corpus.py        # Corpus (singleton that stores all documents)

Document.py      # Base class + RedditDocument + ArxivDocument

Factory.py       # Factory to create the right document type

apis.py          # Calls to Reddit API (PRAW) and arXiv API

main.py          # Entry point of the project

config.py.example  # Template for API keys (to be copied as config.py)

requirements.txt # Python dependencies


How to run the project (step by step)
	1.	Clone the repository

git clone https://github.com/SiamakSm/Python-Search-Motor.git
cd Python-Search-Motor


	2.	(Optional) Create and activate a virtual environment

python -m venv venv
source venv/bin/activate      # macOS / Linux
venv\Scripts\activate         # Windows


	3.	Install dependencies

pip install -r requirements.txt


	4.	Configure API keys

cp config.py.example config.py

Then edit config.py and put your own Reddit credentials.

	5.	Run the program

python main.py

The script fetches data from Reddit and arXiv, saves them into corpus.csv, reloads the corpus, and prints all documents sorted by date.

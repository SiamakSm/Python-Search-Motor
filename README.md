
Python Search Motor – v1 (TD3 → TD5)

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

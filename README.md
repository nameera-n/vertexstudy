Setup Instructions
1) Install Python

Download and install Python 3.11 or newer:

https://www.python.org/downloads/windows/

During installation, make sure to check:

Add Python to PATH
2) Clone the Repository

Open Command Prompt or PowerShell and run:

git clone https://github.com/nameera-n/vertexstudy.git
cd vertexstudy

If Git is not installed, download it here:

https://git-scm.com/download/win

3) Create a Virtual Environment

Run:

python -m venv .venv
4) Activate the Virtual Environment

Run:

.venv\Scripts\activate

You should now see:

(.venv)

at the beginning of the terminal line.

5) Install Project Dependencies

Run:

pip install -r requirements.txt

The installation may take several minutes.

6) Run the Streamlit Dashboard (Recommended)

This is the preferred way to run the project because it provides the full UI and visualization experience.

Run:

streamlit run ui.py

After running the command, Streamlit should automatically open in your browser.

If it does not automatically open, go to:

http://localhost:8501

Example ticker inputs:

NVDA
MSFT
AAPL
META

Example finance article URL:

https://finance.yahoo.com/news/oracle-plans-thousands-job-cuts-180243222.html
Optional: Run the FastAPI Backend

Run:

uvicorn app:app --reload --host 0.0.0.0 --port 8000

Then open:

http://localhost:8000/docs

for the interactive API documentation.

Optional: CLI Usage

Analyze a stock ticker:

python main.py NVDA

Analyze multiple tickers:

python main.py ORCL MSFT NVDA META

Analyze a finance article URL:

python main.py https://finance.yahoo.com/news/oracle-plans-thousands-job-cuts-180243222.html
Troubleshooting

If streamlit is not recognized, run:

pip install streamlit

If torchvision errors appear, run:

pip install torch torchvision torchaudio
Preferred Usage

For demo purposes, it is strongly recommended to run the project through the Streamlit dashboard rather than only using the CLI or API endpoints, since the dashboard contains the primary visualization and interaction features of the project.

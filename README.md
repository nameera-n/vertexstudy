Navigate to project folder

start a virtual environment (not necessary, but good practice)

FOR MAC/LINUX:
pip install torch transformers sentencepiece beautifulsoup4 lxml
(test if working: python3 -c "import transformers; import torch; import sentencepiece; import beautifulsoup4; print('All good')")


Command to run:
python3 main.py TickerNameHere
python3 main.py www.urlofarticle.com/article
python3 main.py Ticker1 Ticker2 Ticker 3

examples:
python3 main.py ORCL
python3 main.py https://finance.yahoo.com/news/oracle-plans-thousands-job-cuts-180243222.html
python3 main.py ORCL MSFT NVDA META
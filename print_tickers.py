import csv

filename = 'Public Companies Feb 18.csv'

def exchange_from_ticker(ticker):
	return ticker.split(':')[-1]

if __name__=="__main__":
	with open(filename, 'U') as f:
		companies = list(csv.DictReader(f))

	tickers = [company['TICKER'] for company in companies]
	exchanges = sorted(list(set(map(exchange_from_ticker, tickers))))

	for exchange in exchanges:
		print exchange
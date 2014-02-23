This script operates on the CSV output of a Bloomberg scraper, data representing
public companies from around the world. Each entry represents a company listed on a
stock exchange somewhere in the world. An example entry from the CSV file:

    'ADDRESS': '1450 Meyerside Drive Suite 500 Mississauga, ON L5T 2N5 Canada',
    'COUNTRY': 'Canada',
    'DESCRIPTION': '[...]',
    'EXCHANGE': 'Frankfurt',
    'INDUSTRY': 'Software',
    'MARKET_CAP': '21.91',
    'NAME': '01 Communique Laboratory Inc',
    'PHONE': '1-905-795-2888',
    'SECTOR': 'Technology',
    'SUB_INDUSTRY': 'Application Software',
    'TICKER': 'DFK:GR',
    'WEBSITE': 'www.01com.com'

Companies are uniquely identified by name and address, and there is a 1:1 correspondence
between name and address. Frequently there are duplicate listings of companies, as they may be
traded on more than one stock exchange in the world. Using the example above of the company
named "01 Communique Laboratory Inc", there are two more listings:

    'ADDRESS': '1450 Meyerside Drive Suite 500 Mississauga, ON L5T 2N5 Canada',
    'COUNTRY': 'Canada',
    'DESCRIPTION': '[...]',
    'EXCHANGE': 'Toronto',
    'INDUSTRY': 'Software',
    'MARKET_CAP': '35.21',
    'NAME': '01 Communique Laboratory Inc',
    'PHONE': '1-905-795-2888',
    'SECTOR': 'Technology',
    'SUB_INDUSTRY': 'Application Software',
    'TICKER': 'ONE:CN',
    'WEBSITE': 'www.01com.com'

    'ADDRESS': '1450 Meyerside Drive Suite 500 Mississauga, ON L5T 2N5 Canada',
    'COUNTRY': 'Canada',
    'DESCRIPTION': '[...]',
    'EXCHANGE': 'OTC  US',
    'INDUSTRY': 'Software',
    'MARKET_CAP': '32.47',
    'NAME': '01 Communique Laboratory Inc',
    'PHONE': '1-905-795-2888',
    'SECTOR': 'Technology',
    'SUB_INDUSTRY': 'Application Software',
    'TICKER': 'OCQLF:US',
    'WEBSITE': 'www.01com.com'

The second listing is on a Canadian stock exchange, and the company's address shows that
the company is based in Canada, so we'll count the first and third listings as duplicates
and remove them.

These other listings may still be interesting, so we'll add on a column called **ALL_TICKERS**
that is a comma-separated list of the **TICKER** values for each of the original duplicate
listings.

Sometimes, a company will be listed on two or more exchanges in its home country, and then
we choose the listing with the bigger **MARKET_CAP** value.

If a company has more than one listing in the CSV file but none of them are on exchanges in
the company's home country, we choose one of the listings arbitrarily to represent the
company.
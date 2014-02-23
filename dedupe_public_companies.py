#!/usr/bin/env python

"""
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
"""

from collections import defaultdict
import csv
import logging
import sys

# A hand-curated list of stock exchange symbols as they appear in the **TICKER** field,
# and the corresponding country where the stock exchange is located.
symbol_to_country = {
	'AB': 'Saudi Arabia',
	'AU': 'Australia',
	'AV': 'Austria',
	'BB': 'Belgium',
	'BZ': 'Brazil',
	'CB': 'Colombia',
	'CH': 'China',
	'CI': 'Chile',
	'CN': 'Canada',
	'DC': 'Denmark',
	'DU': 'Dubai',
	'FH': 'Finland',
	'FP': 'France',
	'G4': 'Denmark',
	'GA': 'Greece',
	'GR': 'Germany',
	'HK': 'Hong Kong',
	'ID': 'Ireland',
	'IJ': 'Indonesia',
	'IM': 'Italy',
	'IN': 'India',
	'IT': 'Israel',
	'JP': 'Japan',
	'KS': 'South Korea',
	'LI': 'United Kingdom',
	'LN': 'United Kingdom',
	'MK': 'Malaysia',
	'MM': 'Mexico',
	'NA': 'Netherlands',
	'NL': 'Nigeria',
	'NO': 'Norway',
	'NZ': 'New Zeland',
	'PM': 'Philippines',
	'PZ': 'United Kingdom',
	'RM': 'Russia',
	'RU': 'Russia',
	'SJ': 'South Africa',
	'SM': 'Spain',
	'SP': 'Singapore',
	'SS': 'Sweden',
	'SW': 'Switzerland',
	'TB': 'Thailand',
	'TI': 'Turkey',
	'TT': 'Taiwan',
	'UH': 'UAE',
	'US': 'United States',
	'VX': 'Switzerland'
}

# Given a set of listings, get the unique **TICKER** values, sort them alphabetically,
# and list them in a string separated by commas. For example, using the listings
# from the top of this file this function would return "DFK:GR, OCQLF:US, ONE:CN"
def tickers_from_listings(listings):
	tickers = sorted(list(set([listing['TICKER'] for listing in listings])))
	return ', '.join(tickers)

if __name__=="__main__":
	# The input and output filenames are given as command-line parameters to this script.
	if len(sys.argv) < 3:
		print "Syntax:"
		print "python {0} input.csv output.csv".format(__file__)
		exit(1)

	input_filename, output_filename = sys.argv[1:3]
	# Logging automatically, verbosely, to a log file named after the input filename.
	logging.basicConfig(filename=input_filename + '.log', level=logging.WARNING)

	# Read the listings in from the original CSV file, containing the data scraped from Bloomberg.
	with open(input_filename, 'U') as f:
		listings = list(csv.DictReader(f))
		logging.info("Loaded {0} company listings from \"{1}\"".format(
			len(listings), input_filename))

	# We'll associate the listings with the unique company names using a dictionary data structure,
	# simplifying the task of finding whether there are duplicate listings.
	listings_by_name = defaultdict(lambda: [])
	for listing in listings:
		listings_by_name[listing['NAME']].append(listing)
	logging.info("Found {0} unique company names.".format(
		len(listings_by_name)))

	deduped_listings = []
	for company_name, company_listings in listings_by_name.items():
		# For each company, uniquely identified by company name, we want
		# a single listing. Initialize this dictionary with 'ALL_TICKERS'
		# containing a comma-separated list of all tickers from all listings
		# for the associated company name.
		main_listing = {'ALL_TICKERS': tickers_from_listings(company_listings)}
		if len(company_listings) == 1:
			logging.info("For company \"{0}\" there is only one listing.".format(
				company_name))
			main_listing.update(company_listings[0])
		else:
			logging.info("Company \"{0}\" has {1} listings, time to deduplicate.".format(
				company_name, len(company_listings)))
			# More than one listing for this company name, now we need to deduplicate.
			home_listings = []
			for listing in company_listings:
				# The contents of TICKER will be something like "DFK:GR", where
				# the part before the colon, "DFK", is the ticker symbol for the company
				# and the part after the colon, "US", signifies the location of
				# the exchange.
				exchange_symbol = listing['TICKER'].split(':')[-1]
				if symbol_to_country[exchange_symbol] in listing['ADDRESS']:
					home_listings.append(listing)
			if len(home_listings) > 1:
				# If there's more than one listing, take the one with the largest
				# market cap.
				logging.info("Found {0} home listings for company \"{1}\", choosing by max market cap.".format(
					len(home_listings), company_name))
				main_listing.update(max(home_listings, key=lambda listing: listing['MARKET_CAP']))
			elif len(home_listings) == 1:
				logging.info("Found 1 home listing for company \"{0}\"".format(company_name))
				main_listing.update(home_listings[0])
			else:
				# There were no home listings found, welp!
				logging.warning("No home listing found for company \"{0}\" located at \"{1}\"".format(
						company_name, company_listings[0]['ADDRESS']))
				logging.warning("Tickers for company \"{0}\" are: {1}".format(
						company_name, main_listing['ALL_TICKERS']))
				# We'll take the first listing, just so we don't forget this company
				# entirely.
				main_listing.update(company_listings[0])
				logging.warning("Picking ticker \"{0}\" as representative listing for company \"{1}\"".format(
					main_listing['TICKER'], company_name))
		deduped_listings.append(main_listing)

	logging.info("Deduplicated to {0} listings, which should be the same as the number of companies ({1}).".format(
		len(deduped_listings), len(listings_by_name)))

	with open(output_filename, 'wb') as f:
		dict_writer = csv.DictWriter(f, fieldnames=deduped_listings[0].keys())
		dict_writer.writeheader()
		dict_writer.writerows(deduped_listings)
		logging.info("Wrote deduped listings to file \"{0}\".".format(output_filename))
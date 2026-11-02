import time
import pandas as pd
import requests
import yfinance as yf

# Get S&P 500 list from Wikipedia
url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
page = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).text
sp500 = pd.read_html(page)[0]

# Select anything thats NOT a bank, insurer, or property company
sp500 = sp500[~sp500['GICS Sector'].isin(['Financials', 'Real Estate'])]

# Values we want from Yahoo
company_metrics = {'enterprise_value': 'enterpriseValue','ebitda': 'ebitda','revenue': 'totalRevenue','revenue_growth': 'revenueGrowth',
'ebitda_margin': 'ebitdaMargins','operating_margin': 'operatingMargins','return_on_assets': 'returnOnAssets',}

# Values we want from Yahoo but from their financial statements
company_statement_metrics = {'capex': ('cashflow', ['Capital Expenditure', 'Purchase Of PPE']), 'total_debt': ('balance_sheet', ['Total Debt']),
'cash': ('balance_sheet', ['Cash And Cash Equivalents','Cash Cash Equivalents And Short Term Investments']), 'total_assets': ('balance_sheet', ['Total Assets'])}

# Gets the most recent metric values from its financial statement
def latest_value(statement, possible_row_names):
    if statement is None or statement.empty:
        return None
    for name in possible_row_names:
        if name in statement.index:
            values = statement.loc[name].dropna()
            if len(values) > 0:
                return float(values.iloc[0])
    return None

all_company_data = []
failed = []

# Loops through for each comapny and gathers data needed
for symbol, sector in zip(sp500['Symbol'], sp500['GICS Sector']):
    yahoo_symbol = symbol.replace('.', '-')

    try:
        ticker = yf.Ticker(yahoo_symbol)
        info = ticker.info
        company_data = {'ticker': symbol, 'sector': sector}

        # Get metric info
        for metric_name, yahoo_name in company_metrics.items():
            company_data[metric_name] = info.get(yahoo_name)

        statements = {'cashflow': ticker.cashflow, 'balance_sheet': ticker.balance_sheet}

        # Loops through each statement metric and checks possible names
        for metric_name, (statement_name, possible_row_names) in company_statement_metrics.items():
            company_data[metric_name] = latest_value(statements[statement_name], possible_row_names)

        # Make capex value positive
        if company_data['capex'] is not None:
            company_data['capex'] = abs(company_data['capex'])

        # If the balance sheet has no 'Total Debt' row just use original value
        if company_data['total_debt'] is None:
            company_data['total_debt'] = info.get('totalDebt')

        all_company_data.append(company_data)

    except Exception as e:
        failed.append(symbol)
        print(symbol, 'failed:', e)

    time.sleep(0.5) 

# Put into a data frame and save to csv
data = pd.DataFrame(all_company_data)
data.to_csv('sp500_snapshot.csv', index=False)

print(len(data), 'companies saved,', len(failed), 'failed')
print('\nMissing values per column:')
print(data.isna().sum())
print(data.head())

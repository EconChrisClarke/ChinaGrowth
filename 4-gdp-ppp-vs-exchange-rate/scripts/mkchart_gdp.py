"""China vs US GDP at market exchange rates and at PPP, latest year from the World Bank API.

Writes data/gdp_ppp_vs_fx.csv (full-precision values) and data/chart_gdp.json (chart config).
"""
import os, json, csv, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
YEAR = '2025'
IND = {'NY.GDP.MKTP.CD': 'Exchange rate', 'NY.GDP.MKTP.PP.CD': 'PPP'}
NAMES = {'CHN': 'China', 'USA': 'U.S.'}

vals = {}
for ind in IND:
    url = f'https://api.worldbank.org/v2/country/CHN;USA/indicator/{ind}?format=json&date={YEAR}&per_page=10'
    meta, rows = json.load(urllib.request.urlopen(url))
    print(ind, 'last updated', meta['lastupdated'])
    for r in rows:
        vals[(ind, r['countryiso3code'])] = r['value']

with open(os.path.join(DATA, 'gdp_ppp_vs_fx.csv'), 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['indicator', 'measure', 'country', 'year', 'gdp'])
    for (ind, c), v in sorted(vals.items()):
        w.writerow([ind, IND[ind], c, YEAR, v])

series = [{'name': NAMES[c], 'data': [round(vals[(ind, c)] / 1e12, 1) for ind in IND]}
          for c in ('CHN', 'USA')]
cfg = {
    "type": "column",
    "headline": "With exchange rate dollars, US economy is bigger. With PPP adjusted dollars, China is",
    "subhead": f"GDP in {YEAR}, trillions of US dollars (exchange rate) and international dollars (PPP)",
    "source": "World Bank, World Development Indicators (NY.GDP.MKTP.CD; NY.GDP.MKTP.PP.CD)",
    "sourceUrl": "https://data.worldbank.org/indicator/NY.GDP.MKTP.PP.CD?locations=CN-US",
    "note": "Exchange-rate GDP converts at market exchange rates. PPP GDP converts at purchasing power parity, "
            "adjusting for price levels; the US is the PPP base, so its two figures are identical.",
    "handle": "@EconChrisClarke",
    "xType": "category",
    "format": {"prefix": "$", "suffix": "T", "decimals": 1},
    "categories": list(IND.values()),
    "barNames": True,
    "valueLabels": True,
    "series": series,
}
with open(os.path.join(DATA, 'chart_gdp.json'), 'w') as f:
    json.dump(cfg, f, indent=2)
print(json.dumps(series))

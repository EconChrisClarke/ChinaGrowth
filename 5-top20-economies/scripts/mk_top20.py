"""Top 20 economies by GDP in 2025, at market exchange rates and at PPP (World Bank WDI).
Writes a CSV of each ranking and a chart config for each."""
import os, json, csv, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
YEAR, N = '2025', 20
SHORT = {'Russian Federation': 'Russia', 'Korea, Rep.': 'South Korea', 'Turkiye': 'Türkiye',
         'Iran, Islamic Rep.': 'Iran', 'Egypt, Arab Rep.': 'Egypt'}

def get(url):
    return json.load(urllib.request.urlopen(url))

# real countries only: aggregates (World, regions, income groups) have region id 'NA'
countries = {c['id'] for c in get('https://api.worldbank.org/v2/country?format=json&per_page=400')[1]
             if c['region']['id'] != 'NA'}

common = dict(
    source="World Bank, World Development Indicators ({ind})",
    handle="@EconChrisClarke", xType="category", type="bar",
    format={"prefix": "$", "suffix": "T", "decimals": 1},
    valueLabels=True, highlight=["China", "United States"],
    categoryColors={"United States": "#1B3A5C"})

charts = {
  'fx': dict(ind='NY.GDP.MKTP.CD',
    headline="At market exchange rates, China and the U.S. are the world's two largest economies",
    subhead=f"GDP in {YEAR}, trillions of US dollars at market exchange rates, top {N} economies",
    note="Converted to US dollars at market exchange rates. Countries only; the World Bank does not report Taiwan."),
  'ppp': dict(ind='NY.GDP.MKTP.PP.CD',
    headline="Adjusted for prices, China and the U.S. are still the world's two largest economies",
    subhead=f"GDP in {YEAR}, trillions of international dollars at purchasing power parity, top {N} economies",
    note="Converted at purchasing power parity, which adjusts for differences in price levels. The US is the PPP base. Countries only; the World Bank does not report Taiwan."),
}

for key, c in charts.items():
    meta, rows = get(f"https://api.worldbank.org/v2/country/all/indicator/{c['ind']}?format=json&date={YEAR}&per_page=400")
    print(c['ind'], 'last updated', meta['lastupdated'])
    rows = sorted((r for r in rows if r['countryiso3code'] in countries and r['value']),
                  key=lambda r: -r['value'])[:N]
    with open(os.path.join(DATA, f'top20_{key}.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(['rank', 'iso3', 'country', 'year', 'gdp'])
        for i, r in enumerate(rows, 1):
            w.writerow([i, r['countryiso3code'], r['country']['value'], YEAR, r['value']])
    names = [SHORT.get(r['country']['value'], r['country']['value']) for r in rows]
    cfg = dict(common, headline=c['headline'], subhead=c['subhead'], note=c['note'],
               source=common['source'].format(ind=c['ind']),
               sourceUrl=f"https://data.worldbank.org/indicator/{c['ind']}",
               categories=names,
               series=[{"name": "GDP", "data": [round(r['value'] / 1e12, 1) for r in rows]}])
    with open(os.path.join(DATA, f'top20_{key}.json'), 'w', encoding='utf-8') as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
    print(' '.join(f"{n}={v}" for n, v in zip(names, cfg['series'][0]['data'])))

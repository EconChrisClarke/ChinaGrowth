"""Growth accounting by income band: China versus its peers (textbook Solow, no human capital).

QUESTION
    At the same level of output per worker, how fast has China grown compared with its peers, and how much of that
    growth came from capital deepening versus the Solow residual (TFP)?

MODEL (undergraduate Solow, per worker)
    y = A * k^alpha              y = Y/L (GDP per worker), k = K/L (capital per worker), L = persons engaged
    g_y = alpha * g_k + g_A      growth = capital deepening + Solow residual
    g_A = g_y - alpha * g_k      the residual: whatever growth capital deepening does not explain
    alpha = 1/3                  (sensitivity to 0.25 and 0.5 is printed at the end)

DATA
    Penn World Table 11.0 (data/pwt110.xlsx, downloaded from Dataverse):
        rgdpna  real GDP at constant 2021 national prices, in 2021 US$   -> y = rgdpna / emp
        rnna    capital stock at constant 2021 national prices, 2021 US$ -> k = rnna / emp
        emp     number of persons engaged
    Comparison economies: the 26 that eventually passed $15,000 GDP per capita (hand-picked, as in the earlier charts).

METHOD (every choice is here, and printed when the script runs)
    1. For each country and year t, compute ANNUAL growth from t-1 to t:  g_y, g_k, capital = alpha*g_k, tfp = g_y - capital.
    2. Assign each country-year to an income band using output per worker at the START of the year (year t-1).
    3. For each country and band, average the annual numbers over the years the country spent in that band.
       (Average annual growth while in the band. No overlapping windows, so no year is counted twice.)
    4. Peers: the MEAN across countries of those country-band averages (one vote per country). A mean is used so that
       capital deepening + TFP = growth holds for the peer bar exactly; a median of each piece would not add up.
       A peer must spend at least MIN_YEARS years in a band to count in that band. Medians are printed as a check.
    5. China: its own country-band average.

CAUTION
    PWT builds capital stocks from 1950 with assumed starting values, so capital growth in the 1950s and 60s partly reflects
    that assumption. The robustness section repeats the comparison using only years from 1970 on.
"""
import os, json, numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ALPHA = 1 / 3
BANDS = [(5_000, 10_000), (10_000, 20_000), (20_000, 30_000), (30_000, 40_000)]   # output per worker, 2021 US$
MIN_YEARS = 3

PEERS = {'USA': 'USA', 'CAN': 'Canada', 'AUS': 'Australia', 'GBR': 'U.K.', 'FRA': 'France', 'DEU': 'Germany', 'ITA': 'Italy',
         'JPN': 'Japan', 'ESP': 'Spain', 'PRT': 'Portugal', 'GRC': 'Greece', 'IRL': 'Ireland', 'KOR': 'South Korea',
         'TWN': 'Taiwan', 'SGP': 'Singapore', 'HKG': 'Hong Kong', 'CHL': 'Chile', 'POL': 'Poland', 'CZE': 'Czechia',
         'HUN': 'Hungary', 'MYS': 'Malaysia', 'TUR': 'Turkey', 'RUS': 'Russia', 'ARG': 'Argentina', 'MEX': 'Mexico', 'THA': 'Thailand'}


def load_pwt():
    """Read the PWT workbook (slow), caching the Data sheet next to the outputs as a pickle (git-ignored)."""
    cache = os.path.join(HERE, '..', 'data', 'pwt110.pkl')
    if os.path.exists(cache):
        return pd.read_pickle(cache)
    d = pd.read_excel(os.path.join(HERE, '..', '..', 'data', 'pwt110.xlsx'), sheet_name='Data')
    d.to_pickle(cache)
    return d


def band_label(lo, hi):
    return '$%d-%dk' % (lo // 1000, hi // 1000)


def annual_accounting(alpha=ALPHA, first_year=None):
    """One row per country-year with growth accounting for the step from year t-1 to t (all in % per year)."""
    d = load_pwt()                                                            # PWT 11.0 main file (Data sheet)
    d = d[d.countrycode.isin(list(PEERS) + ['CHN'])].dropna(subset=['rgdpna', 'rnna', 'emp']).copy()
    d = d.sort_values(['countrycode', 'year'])
    d['y'] = d.rgdpna / d.emp                                                 # output per worker
    d['k'] = d.rnna / d.emp                                                   # capital per worker
    g = d.groupby('countrycode')
    consecutive = (d.year - g.year.shift(1)) == 1                             # only use steps between adjacent years
    d['y_start'] = g.y.shift(1)                                               # income at the start of the year
    d['gy'] = 100 * (np.log(d.y) - np.log(g.y.shift(1)))
    d['gk'] = 100 * (np.log(d.k) - np.log(g.k.shift(1)))
    d['cap'] = alpha * d.gk                                                   # capital deepening contribution
    d['tfp'] = d.gy - d.cap                                                   # the Solow residual
    d = d[consecutive].copy()
    if first_year:
        d = d[d.year >= first_year]
    assert np.allclose(d.cap + d.tfp, d.gy)                                   # identity: the two pieces add to growth
    return d


def band_table(d):
    """Country-by-band averages of the annual numbers, plus the number of years spent in each band."""
    rows = []
    for lo, hi in BANDS:
        b = d[(d.y_start >= lo) & (d.y_start < hi)]
        agg = b.groupby('countrycode').agg(years=('year', 'count'), first=('year', 'min'), last=('year', 'max'),
                                           gy=('gy', 'mean'), cap=('cap', 'mean'), tfp=('tfp', 'mean')).reset_index()
        agg['band'] = band_label(lo, hi)
        rows.append(agg)
    return pd.concat(rows, ignore_index=True)


def summarise(cb):
    """China's row, and the mean and median of the peers' rows, band by band."""
    out = []
    for lo, hi in BANDS:
        lab = band_label(lo, hi)
        b = cb[cb.band == lab]
        ch = b[b.countrycode == 'CHN'].iloc[0]
        pe = b[(b.countrycode != 'CHN') & (b.years >= MIN_YEARS)]
        out.append(dict(band=lab, china_years=int(ch.years), china_span='%d-%d' % (ch['first'], ch['last']),
                        china_gy=ch.gy, china_cap=ch.cap, china_tfp=ch.tfp, n_peers=len(pe),
                        peer_gy=pe.gy.mean(), peer_cap=pe.cap.mean(), peer_tfp=pe.tfp.mean(),
                        med_gy=pe.gy.median(), med_cap=pe.cap.median(), med_tfp=pe.tfp.median()))
    return pd.DataFrame(out)


def gaps(S, kind='peer'):
    """China minus peers (growth / capital / TFP) for each band, as a compact string."""
    return ' | '.join('%s %+.1f/%+.1f/%+.1f' % (r.band, r.china_gy - getattr(r, kind + '_gy'), r.china_cap - getattr(r, kind + '_cap'),
                                               r.china_tfp - getattr(r, kind + '_tfp')) for r in S.itertuples())


if __name__ == '__main__':
    d = annual_accounting()
    cb = band_table(d)
    cb['country'] = cb.countrycode.map(lambda c: PEERS.get(c, 'China'))
    cb.to_csv(os.path.join(HERE, '..', 'data', 'growth_accounting_by_income_band_countries.csv'), index=False)   # every country-band number
    S = summarise(cb)
    S.to_csv(os.path.join(HERE, '..', 'data', 'growth_accounting_by_income_band.csv'), index=False)

    print('SETTINGS: alpha=%.3f, bands=%s, min years for a peer in a band=%d' % (ALPHA, [band_label(*b) for b in BANDS], MIN_YEARS))
    print('\nCHINA: which years fall in each band (income at the start of the year), and the averages (% per year)')
    print(S[['band', 'china_span', 'china_years', 'china_gy', 'china_cap', 'china_tfp']].round(2).to_string(index=False))
    print('\nPEERS, MEAN across countries (what the chart shows) and how many countries are in each band')
    print(S[['band', 'n_peers', 'peer_gy', 'peer_cap', 'peer_tfp']].round(2).to_string(index=False))
    print('\nWho is in each band (peers with at least %d years there):' % MIN_YEARS)
    for lo, hi in BANDS:
        lab = band_label(lo, hi); b = cb[(cb.band == lab) & (cb.countrycode != 'CHN') & (cb.years >= MIN_YEARS)]
        print('  %s (%d): %s' % (lab, len(b), ', '.join(sorted(b.country))))

    print('\nROBUSTNESS: China minus peers, points per year, written growth/capital/TFP')
    print('  baseline, mean of peers:         ' + gaps(S, 'peer'))
    print('  baseline, median of peers:       ' + gaps(S, 'med'))
    for a in (0.25, 0.5):
        Sa = summarise(band_table(annual_accounting(alpha=a)))
        print('  alpha=%.2f, mean of peers:       ' % a + gaps(Sa, 'peer'))
    S70 = summarise(band_table(annual_accounting(first_year=1970)))
    print('  peers from 1970 on only:         ' + gaps(S70, 'peer') + '   (peers per band: %s)' % list(S70.n_peers))

    # Chart configuration: China and the average peer side by side in each band, capital deepening + residual stacked
    cats, cap, tfp = [], [], []
    for r in S.itertuples():
        cats += ['%s China' % r.band, '%s Peers' % r.band]
        cap += [round(r.china_cap, 2), round(r.peer_cap, 2)]
        tfp += [round(r.china_tfp, 2), round(r.peer_tfp, 2)]
    npe = ', '.join(str(n) for n in S.n_peers[:-1]) + ' and ' + str(S.n_peers.iloc[-1])
    cfg = {"type": "column", "xType": "category", "categories": cats, "stacked": True, "yZero": True, "valueLabels": True,
           "highlight": [c for c in cats if c.endswith('China')],
           "headline": "At each income level China outgrows its peers, and most of the gap is faster capital accumulation",
           "subhead": "Growth of GDP per worker by level of GDP per worker: China and the average peer",
           "source": "Penn World Table 11.0 (Feenstra, Inklaar and Timmer); rgdpna, rnna, emp; author's calculations",
           "sourceUrl": "https://www.rug.nl/ggdc/productivity/pwt/",
           "note": "Growth of output per worker = 1/3 x growth of capital per worker + the Solow residual (TFP). Each bar is the average annual growth in years when output per worker (2021 dollars) started in the band. Peers are the average of the 26 comparison economies that eventually passed $15,000 GDP per capita, each counted once, with at least 3 years in the band (%s peers per band)." % npe,
           "format": {"suffix": "", "decimals": 1},
           "series": [{"name": "Capital deepening", "color": "#1B3A5C", "data": cap},
                      {"name": "Total Factor Productivity Growth", "color": "#C71E1D", "data": tfp}]}
    json.dump(cfg, open(os.path.join(HERE, '..', 'data', 'chart_ga_by_income.json'), 'w'))

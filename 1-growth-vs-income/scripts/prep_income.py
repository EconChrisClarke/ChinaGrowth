"""Growth vs income level, Maddison Project Database 2023 (2011 int'l $).
x = GDP per capita in year t; y = trailing 5-year compound growth ending in t."""
import os, pandas as pd, numpy as np
HERE=os.path.dirname(os.path.abspath(__file__))
d=pd.read_csv(os.path.join(HERE,'..','..','data','maddison_gdp_per_capita_owid.csv')).rename(columns={'GDP per capita':'g'})
keep=['United States','Canada','Australia','United Kingdom','France','Germany','Italy','Japan','Spain','Portugal','Greece','Ireland',
 'South Korea','Taiwan','Singapore','Hong Kong','Chile','Poland','Czechia','Hungary','Malaysia','Turkey','Russia','Argentina','Mexico','Thailand','China']
W=5; Y0=1955; XMIN=5000
rows=[]
for e in keep:
    raw=d[d.Entity==e].set_index('Year').g.sort_index()
    s=raw.reindex(range(int(raw.index.min()),int(raw.index.max())+1))
    win=s.loc[max(Y0-W,s.index.min()):]
    assert win.notna().all(), (e,'interpolated years in window',win[win.isna()].index.tolist()[:5])
    cagr=(s/s.shift(W))**(1/W)-1
    for y in s.index:
        if y>=Y0 and not np.isnan(cagr[y]) and s[y]>=XMIN: rows.append((e,y,s[y],cagr[y]*100))
o=pd.DataFrame(rows,columns=['country','year','gdppc','growth5'])
o.to_csv(os.path.join(HERE,'..','data','growth_vs_income.csv'),index=False)
print(o.groupby('country').agg(y0=('year','min'),y1=('year','max'),x0=('gdppc','min'),x1=('gdppc','max')).round(0).to_string())

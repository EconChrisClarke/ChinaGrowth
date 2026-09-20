"""Capital stock and GDP per worker (or per capita), Penn World Table 11.0.
k = rnna / emp ; y = rgdpna / emp, both in constant 2021 national prices converted to 2021 US$
(equal to the current-PPP series cn and cgdpo in the 2021 base year, so levels are comparable across countries).
Set PER=pop for per capita."""
import os, pandas as pd, numpy as np
HERE=os.path.dirname(os.path.abspath(__file__))
PER=os.environ.get('PER','emp')
codes={'United States':'USA','Canada':'CAN','Australia':'AUS','United Kingdom':'GBR','France':'FRA','Germany':'DEU','Italy':'ITA','Japan':'JPN','Spain':'ESP','Portugal':'PRT','Greece':'GRC','Ireland':'IRL','South Korea':'KOR','Taiwan':'TWN','Singapore':'SGP','Hong Kong':'HKG','Chile':'CHL','Poland':'POL','Czechia':'CZE','Hungary':'HUN','Malaysia':'MYS','Turkey':'TUR','Russia':'RUS','Argentina':'ARG','Mexico':'MEX','Thailand':'THA','China':'CHN'}
inv={v:k for k,v in codes.items()}
d=pd.read_excel(os.path.join(HERE,'..','..','data','pwt110.xlsx'),sheet_name='Data')
d=d[d.countrycode.isin(inv)].copy(); d['country']=d.countrycode.map(inv)
d=d.dropna(subset=['rnna','rgdpna',PER])
d['k']=d.rnna/d[PER]; d['y']=d.rgdpna/d[PER]; d['k_over_y']=d.rnna/d.rgdpna
d[['country','countrycode','year','k','y','k_over_y','rnna','rgdpna',PER,'delta','csh_i','hc']].sort_values(['country','year']).to_csv(os.path.join(HERE,'..','data','k_y_per_%s.csv'%PER),index=False)
print(d.groupby('country').agg(y0=('year','min'),y1=('year','max')).T.to_string())

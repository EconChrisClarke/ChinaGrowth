import os, json, pandas as pd, numpy as np
HERE=os.path.dirname(os.path.abspath(__file__))
o=pd.read_csv(os.path.join(HERE,'..','data','growth_vs_income.csv'))
NAMES={'United States':'USA','United Kingdom':'U.K.'}
BW=0.06; MIN_N=8
edges=np.arange(np.log10(5000),np.log10(90000)+BW,BW)
oth=o[o.country!='China'].copy()
oth['bin']=np.digitize(np.log10(oth.gdppc),edges)-1
# one vote per country per income band: country's mean growth in the band, then the median across countries
pc=oth.groupby(['bin','country']).agg(g=('growth5','mean'),x=('gdppc',lambda v:np.exp(np.log(v).mean()))).reset_index()
m=pc.groupby('bin').agg(x=('x','median'),med=('g','median'),n=('country','nunique'))
m=m[m.n>=MIN_N]
def ser(name,df,color=None):
    d={"name":NAMES.get(name,name),"data":[[int(round(r.gdppc)),round(float(r.growth5),2),str(int(r.year))] for r in df.sort_values('year').itertuples()]}
    if color: d['color']=color
    return d
series=[ser(c,o[o.country==c]) for c in sorted(o.country.unique()) if c!='China']
series.append({"name":"Median","color":"#111827","data":[[int(round(r.x)),round(float(r.med),2),"%d countries"%r.n] for r in m.itertuples()]})
series.append(ser('China',o[o.country=='China'],'#C71E1D'))
cfg={"type":"line","xType":"number","xScale":"log","xMin":5000,"xMax":85000,
 "headline":"China's growth slowed as incomes rose, as is standard, but is still ahead of average",
 "subhead":"Average annual GDP per capita growth over the prior 5 years, by GDP per capita (2011 int'l $, log scale)",
 "source":"Maddison Project Database 2023 (via Our World in Data); author's calculations",
 "sourceUrl":"https://www.rug.nl/ggdc/historicaldevelopment/maddison/releases/maddison-project-database-2023",
 "note":"Comparison economies are the 26 that eventually passed $15,000 for the years 1955-2022.",
 "xLabel":"GDP per capita (2011 international dollars)","yLabel":"5-year annualized growth (%)",
 "format":{"suffix":"%","decimals":0},"xFormat":{"prefix":"$","compact":True,"decimals":0},"hoverDecimals":1,
 "range":False,"highlight":["China","Median"],
 "rules":[{"axis":"x","at":15000,"label":"$15,000"}],
 "series":series}
json.dump(cfg,open(os.path.join(HERE,'..','data','chart_income.json'),'w'))
print(len(series),'series; median points',len(m))

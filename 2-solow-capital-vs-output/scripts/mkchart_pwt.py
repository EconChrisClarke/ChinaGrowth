import os, json, pandas as pd, numpy as np
HERE=os.path.dirname(os.path.abspath(__file__))
PER=os.environ.get('PER','emp'); WORD='worker' if PER=='emp' else 'capita'
o=pd.read_csv(os.path.join(HERE,'..','data','k_y_per_%s.csv'%PER))
NAMES={'United States':'USA','United Kingdom':'U.K.'}
BW=0.06; MIN_N=8
oth=o[o.country!='China'].copy()
lo=np.floor(np.log10(oth.k.min())/BW)*BW
oth['bin']=np.floor((np.log10(oth.k)-lo)/BW).astype(int)
pc=oth.groupby(['bin','country']).agg(y=('y','mean'),k=('k',lambda v:np.exp(np.log(v).mean()))).reset_index()
m=pc.groupby('bin').agg(k=('k','median'),y=('y','median'),n=('country','nunique')); m=m[m.n>=MIN_N]
def ser(name,df,color=None):
    d={"name":NAMES.get(name,name),"data":[[int(round(r.k)),int(round(r.y)),str(int(r.year))] for r in df.sort_values('year').itertuples()]}
    if color: d['color']=color
    return d
series=[ser(c,o[o.country==c]) for c in sorted(o.country.unique()) if c!='China']
series.append({"name":"Median","color":"#111827","data":[[int(round(r.k)),int(round(r.y)),"%d countries"%r.n] for r in m.itertuples()]})
series.append(ser('China',o[o.country=='China'],'#C71E1D'))
cfg={"type":"line","xType":"number","xNice":True,"xMin":0,"yMin":0,"xMax":700000,"yMax":160000,"range":False,"highlight":["China","Median"],
 "headline":"At the same capital per worker, China produces about a quarter less than the typical peer",
 "subhead":"GDP per %s against capital stock per %s, 1950-2023 (2021 int'l $)"%(WORD,WORD),
 "source":"Penn World Table 11.0 (Feenstra, Inklaar and Timmer); rnna, rgdpna and %s; author's calculations"%PER,
 "sourceUrl":"https://www.rug.nl/ggdc/productivity/pwt/",
 "note":"Each line is one economy, traced through time. Capital and GDP are at constant 2021 national prices in 2021 US$. Comparison economies are the 26 that eventually passed $15,000 GDP per capita.",
 "xLabel":"Capital stock per %s (2021 int'l $)"%WORD,"yLabel":"GDP per %s (2021 int'l $)"%WORD,
 "format":{"prefix":"$","compact":True,"decimals":0},"xFormat":{"prefix":"$","compact":True,"decimals":0},"hoverDecimals":None,
 "series":series}
cfg={k:v for k,v in cfg.items() if v is not None}
json.dump(cfg,open(os.path.join(HERE,'..','data','chart_%s.json'%PER),'w'))
c=o[o.country=='China'].set_index('year')
# China vs median at China's own k: interpolate median curve
mm=m.sort_values('k')
for yr in [2002,2008,2014,2018,2022,2023]:
    kk=c.k[yr]; 
    if mm.k.min()<=kk<=mm.k.max(): 
        ym=np.interp(kk,mm.k,mm.y); print(yr,'k=%d China y=%d median y=%d gap=%.0f%%'%(kk,c.y[yr],ym,100*(c.y[yr]/ym-1)))
print(len(series),'series; median bands',len(m),'k range',int(mm.k.min()),int(mm.k.max()))

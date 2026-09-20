# ChinaGrowth

Exploring the causes of China's growth trajectory with the textbook Solow model. Three interactive charts, each a single
self-contained HTML file built with the `econ-chart-style` chart engine (click a country or legend entry to highlight it;
each page can also download a PNG).

**Live pages** (GitHub Pages, `https://econchrisclarke.github.io/ChinaGrowth/`):

| # | Chart | Live page | Files |
|---|---|---|---|
| 1 | China's growth slowed as incomes rose, as is standard, but is still ahead of average | [china-growth-vs-income.html](https://econchrisclarke.github.io/ChinaGrowth/china-growth-vs-income.html) | [folder](1-growth-vs-income/) |
| 2 | At the same capital per worker, China produces about a quarter less than the typical peer | [solow-capital-vs-output.html](https://econchrisclarke.github.io/ChinaGrowth/solow-capital-vs-output.html) | [folder](2-solow-capital-vs-output/) |
| 3 | At each income level China outgrows its peers, and most of the gap is faster capital accumulation | [growth-accounting-by-income.html](https://econchrisclarke.github.io/ChinaGrowth/growth-accounting-by-income.html) | [folder](3-growth-accounting-by-income/) |

The HTML files are also in the repository root: [china-growth-vs-income.html](china-growth-vs-income.html),
[solow-capital-vs-output.html](solow-capital-vs-output.html), [growth-accounting-by-income.html](growth-accounting-by-income.html).
(The live links work once GitHub Pages is enabled for the `main` branch.)

## The argument in three steps

1. **China grows fast for its income level, and is slowing along the usual path.** Peers slow as they get richer; China slows too but stays above them.
2. **The Solow diagram.** Plot output per worker against capital per worker. Diminishing returns make the curve concave, and China sits below the peers' median curve, so its capital is producing less output than peers' capital did. That gap is a level difference in what the model calls total factor productivity (TFP).
3. **Growth accounting.** Split growth into capital deepening and the Solow residual, and compare China with peers at the same level of output per worker.

Everything here is descriptive. It uses the plain (unaugmented) Solow model, with no human capital, and it is not a test of the model's predictions.

## 1. Growth against GDP per capita (Maddison data)

- **Data:** Maddison Project Database 2023, GDP per capita in 2011 international dollars, as republished by [Our World in Data](https://ourworldindata.org/grapher/gdp-per-capita-maddison-project-database); original release at [rug.nl/ggdc](https://www.rug.nl/ggdc/historicaldevelopment/maddison/releases/maddison-project-database-2023).
- **Comparison set:** 26 hand-picked economies (advanced economies plus East Asian, Southern and Eastern European, and Latin American catch-up cases) that eventually passed $15,000 GDP per capita. Oil states, tiny economies and successor states are excluded.
- **Growth:** trailing 5-year compound annual growth, `g(t) = (y(t) / y(t-5))^(1/5) - 1`, plotted against GDP per capita in year *t* for 1955-2022 with GDP per capita of at least $5,000. Every year is checked to have real (not interpolated) data in its window.
- **Median line:** income is cut into log10 bands of width 0.06 (about 15%). Within a band each country's growth is averaged, then the median is taken across countries (one vote per country), shown only where at least 8 countries are present.
- **Caveats:** the comparison economies all became rich, which biases their median growth upward at lower incomes; at higher income bands the median comes from recent decades only.

## 2. The Solow diagram: output per worker against capital per worker (Penn World Table)

```
y = A * k^alpha        y = Y/L, k = K/L (per person engaged)
y = rgdpna / emp       k = rnna / emp          (constant 2021 national prices, 2021 US$)
```

- **Data:** [Penn World Table 11.0](https://www.rug.nl/ggdc/productivity/pwt/) (Feenstra, Inklaar and Timmer, 2015, *American Economic Review* 105(10); licensed CC BY 4.0). The raw workbook is `data/pwt110.xlsx`. In 2021, the base year, `rgdpna` and `rnna` equal PWT's current-PPP series, so levels are comparable across countries.
- **Peers' median curve:** bands of log10(k) of width 0.06; within a band each country's average output per worker, then the median across countries (one vote per country), where at least 8 countries are present.
- **Result:** at the same capital per worker, China's GDP per worker is below the median curve by about 28% (2008), 27% (2014), 23% (2018) and 24% (2022).
- **Caveats:**
  - China's PWT capital stock is the softest input. PWT builds it from investment with assumed depreciation and starting values, and a stock rebuilt from PWT's own real investment (anchored in 1990) comes out about 31% lower in 2023. A lower capital stock would shrink the gap.
  - The median curve mixes eras, since peers reached a given capital per worker at different dates and technology improves over time.
  - The axes are pinned ($700k, $160k) and lines are clipped at the edge, so Ireland, Singapore and a few others run off the top.

## 3. Growth accounting by income level (Penn World Table)

```
y = A * k^alpha                        alpha = 1/3
g_y = alpha * g_k + g_A                growth = capital deepening + Solow residual
g_A = g_y - alpha * g_k                the residual (TFP growth)
```

Method (all in `3-growth-accounting-by-income/scripts/growth_accounting_by_income.py`, which prints every choice when run):

1. Annual growth accounting for every country-year, from year *t-1* to *t*.
2. Assign each country-year to a band of output per worker (2021 US$) using income at the start of the year.
3. Average within each country and band over the years the country spent there. No overlapping windows.
4. Peers: the mean across countries (each counted once, at least 3 years in the band). The mean keeps capital + residual = growth exact for the bar; medians are printed as a check.

Results (percentage points per year of growth of output per worker):

| GDP per worker | China: growth = capital + residual | Average peer | Peers in band |
|---|---|---|---|
| $5-10k | 7.9 = 3.3 + 4.6 | 5.0 = 0.9 + 4.1 | 5 |
| $10-20k | 9.7 = 4.0 + 5.7 | 5.3 = 1.7 + 3.6 | 11 |
| $20-30k | 7.0 = 3.4 + 3.6 | 4.8 = 1.8 + 3.0 | 19 |
| $30-40k | 5.3 = 2.7 + 2.6 | 4.4 = 2.0 + 2.5 | 22 |

China's years in the bands: 1997-2005, 2006-2012, 2013-2018 and 2019-2023.

Caveats:

- **Capital share.** At alpha = 0.25 the $10-20k gap is mostly productivity. At alpha = 0.5 capital explains more than the whole gap in three bands, and China's residual advantage turns slightly negative.
- **Early peer data.** PWT builds capital stocks from 1950 with assumed starting values, so 1950s and 60s peer capital growth is unreliable. Restricting peers to 1970 onward leaves only 1, 4, 9 and 12 peers per band. The lowest band is effectively five East Asian economies from the 1950s to 1970s, so treat it with caution.
- **Selection.** All peers eventually became rich, which biases their growth upward at lower incomes.
- **The residual is a catch-all.** It includes technology, human capital, hours, misallocation, quality change and measurement error.

## Repository layout

```
china-growth-vs-income.html           chart 1 (live, self-contained)
solow-capital-vs-output.html          chart 2
growth-accounting-by-income.html      chart 3
data/                                 raw source data (Maddison via OWID; PWT 11.0 workbook)
tools/                                the chart builder, template and logo used to build every page
<n>-<chart>/scripts/                  the scripts that compute each chart's numbers and write its config
<n>-<chart>/data/                     derived data and the chart configuration (JSON)
```

## Reproducing a chart

Requires Python with `pandas`, `numpy` and `openpyxl`. Reading the PWT workbook takes about a minute the first time.
From the repository root:

```bash
# 1. growth against GDP per capita
(cd 1-growth-vs-income/scripts && python prep_income.py && python mkchart_income.py)
python tools/build_chart.py --config 1-growth-vs-income/data/chart_income.json --template tools/chart-template.html --out china-growth-vs-income.html

# 2. the Solow diagram
(cd 2-solow-capital-vs-output/scripts && python prep_pwt.py && python mkchart_pwt.py)
python tools/build_chart.py --config 2-solow-capital-vs-output/data/chart_emp.json --template tools/chart-template.html --out solow-capital-vs-output.html

# 3. growth accounting by income level
(cd 3-growth-accounting-by-income/scripts && python growth_accounting_by_income.py)
python tools/build_chart.py --config 3-growth-accounting-by-income/data/chart_ga_by_income.json --template tools/chart-template.html --out growth-accounting-by-income.html
```

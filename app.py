import requests as rq, pandas as pd, plotly.express as px, re, streamlit as st, time, json
st.set_page_config(layout="wide")
# st.markdown('<style>.css-4z1n4l {display:none}</style',unsafe_allow_html=True)
headers_for_scraping = {"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                        "Accept-Encoding":"gzip, deflate",
                        "Accept-Language":"en-GB,en;q=0.9,en-US;q=0.8,ml;q=0.7",
                        "Connection":"keep-alive",
                        "Referer":"https://www.nasdaq.com/market-activity/quotes/historical",
                        "Upgrade-Insecure-Requests":"1",
                        "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36"} 
tickers = ['AAPL', 'AMZN', 'ASML', 'AVGO', 'AZN', 'COST', 'CSCO', 'GOOG', 'GOOGL', 'META', 'MSFT', 'NVDA', 'PEP', 'TSLA']

pl = st.empty()

chart, filter = st.columns([5,1])
with filter:
    c = st.selectbox('Ticker', options=tickers)

with filter:
    resp = rq.get('https://www.timeapi.io/api/Time/current/zone?timeZone=America/New_York', headers={'accept':'application/json'})
    st.text('Exact time on NY exchange:\n' + json.loads(resp.text)['dateTime'].split('T')[1].split('.')[0])

for i in range(50):
    with pl.container():


        resp = rq.get(f'https://api.nasdaq.com/api/quote/{c}/chart?assetclass=stocks&fromdate=2012-01-01&todate=2023-03-31', headers=headers_for_scraping, verify=True)

        current_ticker_df = pd.read_json(re.search('\[.*\]', resp.text).group(), orient = 'records').drop(columns=['z'])
        current_ticker_df['x'] = pd.to_datetime(current_ticker_df['x'], unit='ms')
        current_ticker_df.rename(columns={'x':'Date','y':'Price, $'}, inplace=True)

        with chart:
            st.plotly_chart(px.line(current_ticker_df, x='Date', y='Price, $'), use_container_width=True)
        time.sleep(0.375)
        st.experimental_rerun()
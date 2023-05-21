import requests as rq, pandas as pd, plotly.express as px, re, streamlit as st, time, json, datetime
from tensorflow import keras
import numpy as np
import cs as scaling

st.set_page_config(
    page_title="Polycast",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={'About': 'Developed by @sixxio as diploma project in 2023.'}
    # primary_color='#0078FF',
    # background_color='#F5F5F5',
    # font='#262730'
)
st.markdown('<style>.css-4z1n4l {display:none}</style',unsafe_allow_html=True)
headers_for_scraping = {"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                        "Accept-Encoding":"gzip, deflate",
                        "Accept-Language":"en-GB,en;q=0.9,en-US;q=0.8,ml;q=0.7",
                        "Connection":"keep-alive",
                        "Referer":"https://www.nasdaq.com/market-activity/quotes/historical",
                        "Upgrade-Insecure-Requests":"1",
                        "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36"} 
# tickers = ['AAPL', 'AMZN', 'ASML', 'AVGO', 'AZN', 'COST', 'CSCO', 'GOOG', 'GOOGL', 'META', 'MSFT', 'NVDA', 'PEP', 'TSLA']
file = open('tickers_by_size.json','r')
tickers = json.loads(file.read())
file.close()

pl = st.empty()

chart, filter = st.columns([5,1])
with filter:
    hh = st.selectbox('Группа компаний', options=list(tickers.keys()))
    c = st.selectbox('Компания', options=tickers[hh])
    h = st.slider('Горизонт прогнозирования', min_value=1, max_value=30, step=1)
df = st.expander('Смотреть данные')

# fetching and parsing data
resp = rq.get(f'https://api.nasdaq.com/api/quote/{c}/chart?assetclass=stocks&fromdate=2013-02-02&todate={datetime.datetime.now().strftime("%Y-%m-%d")}', headers=headers_for_scraping, verify=True)
smth = json.loads(re.search('\[.*\]', resp.text).group())
cur_tick_data = pd.DataFrame([smth[k]['z'] for k in range(len(smth))])

# providing dtypes
for i in ['open', 'close', 'high','low','volume']:
    cur_tick_data[i] = pd.to_numeric(cur_tick_data[i].str.replace(',',''))
cur_tick_data['dateTime'] = pd.to_datetime(cur_tick_data['dateTime'])

cur_tick_data = cur_tick_data.rename(columns={'dateTime': 'Дата', 'close':'Стоимость при закрытии торгов, $', 'open':'Стоимость при открытии торгов, $',\
                                            'volume':'Объем', 'low':'Минимальная стоимость, $', 'high':'Максимальная стоимость, $'}).drop(columns='value')
cur_tick_data['Тип'] = 'История'
with df:
    st.dataframe(cur_tick_data, use_container_width=True)

# extracting data
date = datetime.datetime.strptime(str(cur_tick_data['Дата'].iloc[-1]), '%Y-%m-%d %H:%M:%S')
dates = [(date + datetime.timedelta(days=i)).strftime('%m-%d-%Y') for i in range(h+1)]
prices = cur_tick_data['Стоимость при закрытии торгов, $'].iloc[-20:].tolist()

# loading model and scaler
model = keras.models.load_model('11.h5')
cs = scaling.CustomScaler((13.947505579, 180.33))
for i in range(h):
    prices += cs.unscale(model.predict(cs.scale(np.array(prices[-20:]).reshape((1,20,1)))).reshape(-1)).tolist()
    print(cs.unscale(model.predict(cs.scale(np.array(prices[-20:]).reshape((1,20,1)))).reshape(-1)))

# concating data
future = pd.DataFrame({'Дата' : dates, 'Стоимость при закрытии торгов, $': prices[19:], 'Тип': ['Прогноз']*(h+1)})
future['Дата'] = pd.to_datetime(future['Дата'])
current_ticker_df = pd.concat([cur_tick_data, future])

# plotting
with chart:
    st.plotly_chart(px.line(current_ticker_df, x='Дата', y='Стоимость при закрытии торгов, $', color = 'Тип'), use_container_width=True)
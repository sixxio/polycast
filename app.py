# importing modules
import cs as scaling, requests as rq, pandas as pd, plotly.express as px, re, streamlit as st, numpy as np, json, datetime
from tensorflow import keras

# setting page params
st.set_page_config(
    page_title="Polycast",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={'About': 'Developed by @sixxio as diploma project in 2023.'}
)

# disabling loading pic
st.markdown('<style>.css-4z1n4l {display:none}</style', unsafe_allow_html = True)

# defining headers for parsing
headers = {"Accept":"text/html", "Accept-Language":"en-US", "Referer":"https://www.nasdaq.com/", "User-Agent":"Chrome/64.0.3282.119"} 

# importing tickers
file = open('tickers.json','r')
tickers = json.loads(file.read())
file.close()

# defining interface elements
chart, filter = st.columns([5,1])
with filter:
    hh = st.selectbox('Группа компаний', options=list(tickers.keys()))
    c = st.selectbox('Компания', options=tickers[hh])
    h = st.slider('Горизонт прогнозирования', min_value=1, max_value=30, step=1)
df = st.expander('Смотреть данные')

# fetching and parsing data from nasdaq
resp = rq.get(f'https://api.nasdaq.com/api/quote/{c}/chart?assetclass=stocks&fromdate=2013-02-02&todate={datetime.datetime.now().strftime("%Y-%m-%d")}', headers=headers, verify=True)
smth = json.loads(re.search('\[.*\]', resp.text).group())
cur_tick_data = pd.DataFrame([smth[k]['z'] for k in range(len(smth))]).drop(columns='value')

# providing dtypes, renaming columns
for i in ['open', 'close', 'high','low','volume']:
    cur_tick_data[i] = pd.to_numeric(cur_tick_data[i].str.replace(',',''))
cur_tick_data['dateTime'] = pd.to_datetime(cur_tick_data['dateTime'])
cur_tick_data.columns = ['Максимальная стоимость, $', 'Минимальная стоимость, $', 'Стоимость при открытии торгов, $', 'Стоимость при закрытии торгов, $', 'Объем', 'Дата']
cur_tick_data['Тип'] = 'История'

# showing df with historical data
with df:
    st.dataframe(cur_tick_data, use_container_width=True)

# extracting initial data for forecasting
date = datetime.datetime.strptime(str(cur_tick_data['Дата'].iloc[-1]), '%Y-%m-%d %H:%M:%S')
dates = [(date + datetime.timedelta(days=i)).strftime('%m-%d-%Y') for i in range(h+1)]
prices = cur_tick_data['Стоимость при закрытии торгов, $'].iloc[-20:].tolist()

# loading model and scaler, forecasting price
model = keras.models.load_model('11.h5')
cs = scaling.CustomScaler((13.947505579, 180.33)).fit(cur_tick_data['Стоимость при закрытии торгов, $'])
for i in range(h):
    prices += cs.unscale(model.predict(cs.scale(np.array(prices[-20:]).reshape((1,20,1))), verbose=0).reshape(-1)).tolist()

# concating forecast to historical data
future = pd.DataFrame({'Дата' : dates, 'Стоимость при закрытии торгов, $': prices[19:], 'Тип': ['Прогноз']*(h+1)})
future['Дата'] = pd.to_datetime(future['Дата'])
current_ticker_df = pd.concat([cur_tick_data, future])

# plotting chart with forecast
with chart:
    st.plotly_chart(px.line(current_ticker_df, x='Дата', y='Стоимость при закрытии торгов, $', color = 'Тип'), use_container_width=True)

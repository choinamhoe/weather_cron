import json, requests, datetime
from sqlalchemy import create_engine, text
import pandas as pd

"""
wheater DB 안에 asos_hour 테이블에 현재 시간에 대한 데이터를 가져와 삽입하는 코드
"""

# type1
with open("/app/api.json", "r",encoding="utf-8") as f:
    key_dict = json.load(f)
# type2
# f=open("./src/api.json")
# key_dict=json.load(f)

db_info = "mysql+pymysql://web:web1234@localhost:13306"
engine = create_engine(db_info,connect_args={}) 
con = engine.connect()

BASE_URL = "https://apihub.kma.go.kr/api/typ01/url"
SUB_URL = "kma_sfctm3.php"
key = key_dict["KMA_KEY"]

st_dt = datetime.datetime.now() - pd.to_timedelta(1, unit="hour")
st_dt = pd.to_datetime(st_dt).strftime("%Y%m%d%H%M")
ed_dt = pd.to_datetime(datetime.datetime.now()).strftime("%Y%m%d%H%M")

url = f"{BASE_URL}/{SUB_URL}?tm1={st_dt}&tm2={ed_dt}&help=1&authKey={key}"
stations=["185"]

url += f"&stn={':'.join(stations)}" # type 1
# url = url + f"&stn={':'.join(stations)}" # type2
res = requests.get(url)
source = res.text.split("\n")
_source = list()
for line in source:
    _source.append(line.split())

hour_df=pd.DataFrame(_source[54:-2],columns=[i[2] for i in _source[4:50]])
hour_df=hour_df[["STN","TM","TA","PR","HM","WS","WD"]].copy()
hour_df["STN"] = hour_df["STN"].astype(int)
hour_df["TM"] = pd.to_datetime(hour_df["TM"]).dt.strftime("%Y-%m-%d %H:%M:%S")
hour_df["TA"] = hour_df["TA"].astype(float)
hour_df["PR"] = hour_df["PR"].astype(float)
hour_df["HM"] = hour_df["HM"].astype(float)
hour_df["WS"] = hour_df["WS"].astype(float)
hour_df["WD"] = hour_df["WD"].astype(int)


columns = pd.read_sql("SHOW COLUMNS FROM weather.ASOS_HOUR;", con=engine).Field.values
hour_df.columns = columns

db_info = "mysql+pymysql://web:web1234@localhost:13306/weather"
engine = create_engine(db_info,connect_args={}) 
con = engine.connect()
try:
    print(1)
    hour_df.to_sql("ASOS_HOUR", con=engine, if_exists="append", index=False)
except:
    print(2)
    pass




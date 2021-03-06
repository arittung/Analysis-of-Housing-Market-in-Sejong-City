# -*coding:utf-8 -*-


import pathlib
import random
from functools import reduce
from collections import defaultdict

import pandas as pd
import geopandas as gpd
import folium
import shapely
import numpy as np
from IPython.display import display
import matplotlib.pyplot as plt
from tqdm.notebook import tqdm
import xgboost
import sklearn.cluster
import tensorflow as tf
import matplotlib as mpl
import seaborn as sns

from pandas import DataFrame
from geoband import API
from folium import Map, CircleMarker, Vega, Popup
from vincent import Bar
import math

## 제공된 데이터

input_path = pathlib.Path('./input')
if not input_path.is_dir():
    input_path.mkdir()

from geoband.API import *

GetCompasData('SBJ_2102_001', '1', '1.세종시_전유부.csv')
GetCompasData('SBJ_2102_001', '2', '2.세종시_표제부.csv')
GetCompasData('SBJ_2102_001', '3', '3.세종시_아파트(매매)_실거래가.csv')
GetCompasData('SBJ_2102_001', '4', '4.세종시_연립다세대(매매)_실거래가.csv')
GetCompasData('SBJ_2102_001', '5', '5.세종시_단독다가구(매매)_실거래가.csv')
GetCompasData('SBJ_2102_001', '6', '6.세종시_오피스텔(매매)_실거래가.csv')
GetCompasData('SBJ_2102_001', '7', '7.세종시_아파트(전월세)_실거래가.csv')
GetCompasData('SBJ_2102_001', '8', '8.세종시_연립다세대(전월세)_실거래가.csv')
GetCompasData('SBJ_2102_001', '9', '9.세종시_단독다가구(전월세)_실거래가.csv')
GetCompasData('SBJ_2102_001', '10', '10.세종시_오피스텔(전월세)_실거래가.csv')
GetCompasData('SBJ_2102_001', '11', '11.세종시_상업업무용(매매)_실거래가.csv')
GetCompasData('SBJ_2102_001', '12', '12.세종시_토지(매매)_실거래가.csv')
GetCompasData('SBJ_2102_001', '13', '13.세종시_분양권_실거래가.csv')
GetCompasData('SBJ_2102_001', '14', '14.세종시_상권정보.csv')
GetCompasData('SBJ_2102_001', '15', '15.세종시_상권정보_업종코드.csv')
GetCompasData('SBJ_2102_001', '16', '16.세종시_사업체_매출정보.geojson')
GetCompasData('SBJ_2102_001', '17', '17.세종시_사업체_매출정보.csv')
GetCompasData('SBJ_2102_001', '18', '18.세종시_개별공시지가(2017~2020).csv')
GetCompasData('SBJ_2102_001', '19', '19.세종시_연령별_거주인구정보_격자.geojson')
GetCompasData('SBJ_2102_001', '20', '20.세종시_전입자수.csv')
GetCompasData('SBJ_2102_001', '21', '21.세종시_전출자수.csv')
GetCompasData('SBJ_2102_001', '22', '22.세종시_연령별_인구현황.csv')
GetCompasData('SBJ_2102_001', '23', '23.세종시_도로명주소_건물.geojson')
GetCompasData('SBJ_2102_001', '24', '24.세종시_건축물연면적_격자.geojson')
GetCompasData('SBJ_2102_001', '25', '25.세종시_가구_월평균_소비지출액.csv')
GetCompasData('SBJ_2102_001', '26', '26.세종시_거주기간.csv')
GetCompasData('SBJ_2102_001', '27', '27.세종시_월평균_가구소득.csv')
GetCompasData('SBJ_2102_001', '28', '28.세종시_지역별_세대원수별_세대수.csv')
GetCompasData('SBJ_2102_001', '29', '29.세종시_거주의사(향후).csv')
GetCompasData('SBJ_2102_001', '30', '30.세종시_법정경계(시군구).geojson')
GetCompasData('SBJ_2102_001', '31', '31.세종시_법정경계(읍면동).geojson')
GetCompasData('SBJ_2102_001', '32', '32.세종시_행정경계(읍면동).geojson')
GetCompasData('SBJ_2102_001', '33', '33.세종시_지적도.geojson')
GetCompasData('SBJ_2102_001', '34', '34.세종시_건물분포_이미지.zip')

for path in list(input_path.glob('*.csv')) + list(input_path.glob('*.geojson')):
    print(path)

## 지역별 매매 평균값

# 자료 불러오기
아파트_매매 = pd.read_csv(input_path.joinpath('3.세종시_아파트(매매)_실거래가.csv'), encoding='utf-8')
아파트_매매

# 세종 특별자치시 없애기
for i in range(len(아파트_매매['시군구'])):
    아파트_매매['시군구'][i] = 아파트_매매['시군구'][i][7:]

# col 확인
아파트_매매.columns

# 주소별 거래금액 평균 구하기
아파트_매매['거래금액(만원)'] = 아파트_매매['거래금액(만원)'].apply(lambda x: float(x.split()[0].replace(',', '')))
data_아파트 = 아파트_매매.groupby('시군구')['거래금액(만원)'].mean()
data_아파트

# 그래프 한글깨짐 방지
import matplotlib

matplotlib.font_manager._rebuild()
plt.rc("font", family="Malgun Gothic")

# 지역 별 평균 가격 그래프
ax = data_아파트.plot(kind='bar', title='지역별 아파트 평균 가격', figsize=(15, 5), legend=True, fontsize=10, color='indigo')
ax.set_xlabel('지역', fontsize=12)
ax.set_ylabel('아파트 평균 가격', fontsize=12)
ax.legend(['평균가격'], fontsize=12)

# 자료 불러오기
연립다세대_매매 = pd.read_csv(input_path.joinpath('4.세종시_연립다세대(매매)_실거래가.csv'), thousands=',', encoding='utf-8')
연립다세대_매매

# 세종 특별자치시 없애기
for i in range(len(연립다세대_매매['시군구'])):
    연립다세대_매매['시군구'][i] = 연립다세대_매매['시군구'][i][7:]

# col 확인
연립다세대_매매.columns

# 주소별 거래금액 평균 구하기
data_연립다세대 = 연립다세대_매매.groupby('시군구')['거래금액(만원)'].mean()
data_연립다세대

# 그래프 한글깨짐 방지
import matplotlib

matplotlib.font_manager._rebuild()
plt.rc("font", family="Malgun Gothic")

# 지역 별 평균 가격 그래프
ax = data_연립다세대.plot(kind='bar', title='지역별 연립다세대 평균 가격', figsize=(15, 5), legend=True, fontsize=10,
                     color='deepskyblue')
ax.set_xlabel('지역', fontsize=12)
ax.set_ylabel('연립다세대 평균 가격', fontsize=12)
ax.legend(['평균가격'], fontsize=12)

# 자료 불러오기
단독다가구_매매 = pd.read_csv(input_path.joinpath('5.세종시_단독다가구(매매)_실거래가.csv'), encoding='utf-8')
단독다가구_매매

# 세종 특별자치시 없애기
for i in range(len(단독다가구_매매['시군구'])):
    단독다가구_매매['시군구'][i] = 단독다가구_매매['시군구'][i][7:]

# col 확인
단독다가구_매매.columns

# 주소별 거래금액 평균 구하기
단독다가구_매매['거래금액(만원)'] = 단독다가구_매매['거래금액(만원)'].apply(lambda x: float(x.split()[0].replace(',', '')))
data_단독다가구 = 단독다가구_매매.groupby('시군구')['거래금액(만원)'].mean()
data_단독다가구

# 그래프 한글깨짐 방지
import matplotlib

matplotlib.font_manager._rebuild()
plt.rc("font", family="Malgun Gothic")

# 지역 별 평균 가격 그래프
ax = data_단독다가구.plot(kind='bar', title='지역별 단독다가구 평균 가격', figsize=(80, 15), legend=True, fontsize=32,
                     color='midnightblue')
ax.set_xlabel('지역', fontsize=30)
ax.set_ylabel('단독다가구 평균 가격', fontsize=30)
ax.legend(['평균 가격'], fontsize=30)

# 자료 불러오기
오피스텔_매매 = pd.read_csv(input_path.joinpath('6.세종시_오피스텔(매매)_실거래가.csv'), encoding='utf-8')
오피스텔_매매

# 세종 특별자치시 없애기
for i in range(len(오피스텔_매매['시군구'])):
    오피스텔_매매['시군구'][i] = 오피스텔_매매['시군구'][i][7:]

# col 확인
오피스텔_매매.columns

# 주소별 거래금액 평균 구하기
오피스텔_매매['거래금액(만원)'] = 오피스텔_매매['거래금액(만원)'].apply(lambda x: float(x.split()[0].replace(',', '')))
data_오피스텔 = 오피스텔_매매.groupby('시군구')['거래금액(만원)'].mean()
data_오피스텔

# 그래프 한글깨짐 방지
import matplotlib

matplotlib.font_manager._rebuild()
plt.rc("font", family="Malgun Gothic")

# 지역 별 평균 가격 그래프
ax = data_오피스텔.plot(kind='bar', title='지역별 오피스텔 평균 가격', figsize=(15, 5), legend=True, fontsize=10,
                    color='palevioletred')
ax.set_xlabel('지역', fontsize=12)
ax.set_ylabel('오피스텔 평균 가격', fontsize=12)
ax.legend(['평균가격'], fontsize=12)

## 지역별 전, 월세 평균값

# 자료 불러오기
아파트_전월세 = pd.read_csv(input_path.joinpath('7.세종시_아파트(전월세)_실거래가.csv'), thousands=',', encoding='utf-8'' )
아파트_전월세

# 행 확인
아파트_전월세.columns

# 세종특별자치시 없애기
for i in range(len(아파트_전월세['시군구'])):
    아파트_전월세['시군구'][i] = 아파트_전월세['시군구'][i][7:]

# 지역마다 전,월세 평균
data_아파트_전월세 = 아파트_전월세.groupby(['시군구', '전월세구분'])[['보증금(만원)', '월세(만원)']].mean()
data_아파트_전월세 = data_아파트_전월세.unstack().fillna(0)
data_아파트_전월세

data_아파트_전월세_월세보증금 = data_아파트_전월세['보증금(만원)', '월세']
data_아파트_전월세_월세 = data_아파트_전월세['월세(만원)', '월세']
data_아파트_전세 = data_아파트_전월세['보증금(만원)', '전세']

# data_아파트_전월세['보증금(만원)','전세'] = data_아파트_전세
del (data_아파트_전월세['월세(만원)', '전세'])
del (data_아파트_전월세['보증금(만원)', '전세'])

round(data_아파트_전월세, 2)

# 그래프 한글깨짐 방지
matplotlib.font_manager._rebuild()
plt.rc("font", family="Malgun Gothic")

# 지역 별 평균 가격 그래프
ax = data_아파트_전월세.plot(kind='bar', title='지역별 아파트 전월세 평균 가격', figsize=(15, 5), legend=True, fontsize=10,
                       color=['dodgerblue', 'crimson'])
plt.plot(data_아파트_전세, linestyle='--', color='orangered')
ax.set_xlabel('지역', fontsize=12)
ax.set_ylabel('아파트 평균 가격(전월세)', fontsize=12)
ax.legend(['전세 가격', '월세보증금', '월세 가격'], fontsize=12)

for i, v in enumerate(data_아파트_전월세['월세(만원)', '월세']):
    ax.text(i - 0.1, v + v * 20, str(round(v, 1)))

# 자료 불러오기
연립다세대_전월세 = pd.read_csv(input_path.joinpath('8.세종시_연립다세대(전월세)_실거래가.csv'), thousands=',', encoding='utf-8')
연립다세대_전월세

# 행 확인
연립다세대_전월세.columns

# 세종특별자치시 없애기
for i in range(len(연립다세대_전월세['시군구'])):
    연립다세대_전월세['시군구'][i] = 연립다세대_전월세['시군구'][i][7:]

# 지역마다 전,월세 평균
data_연립다세대_전월세 = 연립다세대_전월세.groupby(['시군구', '전월세구분'])[['보증금(만원)', '월세(만원)']].mean()
data_연립다세대_전월세 = data_연립다세대_전월세.unstack().fillna(0)
data_연립다세대_전월세

data_연립다세대_전월세_월세보증금 = data_연립다세대_전월세['보증금(만원)', '월세']
data_연립다세대_전월세_월세 = data_연립다세대_전월세['월세(만원)', '월세']
data_연립다세대_전세 = data_연립다세대_전월세['보증금(만원)', '전세']

# data_연립다세대_전월세['보증금(만원)','전세'] = data_연립다세대_전세
del (data_연립다세대_전월세['월세(만원)', '전세'])
del (data_연립다세대_전월세['보증금(만원)', '전세'])

round(data_연립다세대_전월세, 2)

# 그래프 한글깨짐 방지
matplotlib.font_manager._rebuild()
plt.rc("font", family="Malgun Gothic")

# 지역 별 평균 가격 그래프
ax = data_연립다세대_전월세.plot(kind='bar', title='지역별 연립다세대 전월세 평균 가격', figsize=(15, 5), legend=True, fontsize=10,
                         color=['dodgerblue', 'crimson'])
plt.plot(data_연립다세대_전세, linestyle='--', color='orangered')
ax.set_xlabel('지역', fontsize=12)
ax.set_ylabel('연립다세대 평균 가격(전월세)', fontsize=12)
ax.legend(['전세 가격', '월세보증금', '월세 가격'], fontsize=12)

for i, v in enumerate(data_연립다세대_전월세['월세(만원)', '월세']):
    ax.text(i - 0.1, v + v * 20, str(round(v, 1)))

# 자료 불러오기
단독다가구_전월세 = pd.read_csv(input_path.joinpath('9.세종시_단독다가구(전월세)_실거래가.csv'), thousands=',', encoding='utf-8')
단독다가구_전월세

# 행 확인
단독다가구_전월세.columns

# 세종특별자치시 없애기
for i in range(len(단독다가구_전월세['시군구'])):
    단독다가구_전월세['시군구'][i] = 단독다가구_전월세['시군구'][i][7:]

# 지역마다 전,월세 평균
data_단독다가구_전월세 = 단독다가구_전월세.groupby(['시군구', '전월세구분'])[['보증금(만원)', '월세(만원)']].mean()
data_단독다가구_전월세 = data_단독다가구_전월세.unstack().fillna(0)
data_단독다가구_전월세

data_단독다가구_전월세_월세보증금 = data_단독다가구_전월세['보증금(만원)', '월세']
data_단독다가구_전월세_월세 = data_단독다가구_전월세['월세(만원)', '월세']
data_단독다가구_전세 = data_단독다가구_전월세['보증금(만원)', '전세']

# data_단독다가구_전월세['보증금(만원)','전세'] = data_단독다가구_전세
del (data_단독다가구_전월세['월세(만원)', '전세'])
del (data_단독다가구_전월세['보증금(만원)', '전세'])

round(data_단독다가구_전월세, 2)

# 그래프 한글깨짐 방지
matplotlib.font_manager._rebuild()
plt.rc("font", family="Malgun Gothic")

# 지역 별 평균 가격 그래프
ax = data_단독다가구_전월세.plot(kind='bar', title='지역별 단독다가구 전월세 평균 가격', figsize=(80, 15), legend=True, fontsize=32,
                         color=['dodgerblue', 'crimson'])
ax.plot(data_단독다가구_전세, linestyle='--', color='orangered')
ax.set_xlabel('지역', fontsize=30)
ax.set_ylabel('단독다가구 평균 가격', fontsize=30)
ax.legend(['전세 가격', '월세보증금', '월세 가격'], fontsize=20)
ax.title.set_size(35)

for i, v in enumerate(data_단독다가구_전월세['월세(만원)', '월세']):
    ax.text(i - 0.1, v + v * 20, str(v), size=30)

# 자료 불러오기
오피스텔_전월세 = pd.read_csv(input_path.joinpath('10.세종시_오피스텔(전월세)_실거래가.csv'), thousands=',', encoding='utf-8')
오피스텔_전월세

# 행 확인
오피스텔_전월세.columns

# 세종특별자치시 없애기
for i in range(len(오피스텔_전월세['시군구'])):
    오피스텔_전월세['시군구'][i] = 오피스텔_전월세['시군구'][i][7:]

# 지역마다 전,월세 평균
data_오피스텔_전월세 = 오피스텔_전월세.groupby(['시군구', '전월세구분'])[['보증금(만원)', '월세(만원)']].mean()
data_오피스텔_전월세 = data_오피스텔_전월세.unstack().fillna(0)
data_오피스텔_전월세

data_오피스텔_전월세_월세보증금 = data_오피스텔_전월세['보증금(만원)', '월세']
data_오피스텔_전월세_월세 = data_오피스텔_전월세['월세(만원)', '월세']
data_오피스텔_전세 = data_오피스텔_전월세['보증금(만원)', '전세']

# data_오피스텔_전월세['보증금(만원)','전세'] = data_오피스텔_전세
del (data_오피스텔_전월세['월세(만원)', '전세'])
del (data_오피스텔_전월세['보증금(만원)', '전세'])

round(data_오피스텔_전월세, 2)

# 그래프 한글깨짐 방지
matplotlib.font_manager._rebuild()
plt.rc("font", family="Malgun Gothic")

# 지역 별 평균 가격 그래프
ax = data_오피스텔_전월세.plot(kind='bar', title='지역별 오피스텔 전월세 평균 가격', figsize=(15, 5), legend=True, fontsize=10,
                        color=['dodgerblue', 'crimson'])
plt.plot(data_오피스텔_전세, linestyle='--', color='orangered')
ax.set_xlabel('지역', fontsize=12)
ax.set_ylabel('오피스텔 평균 가격(전월세)', fontsize=12)
ax.legend(['전세 가격', '월세보증금', '월세 가격'], fontsize=12)

for i, v in enumerate(data_오피스텔_전월세['월세(만원)', '월세']):
    ax.text(i + 0.05, v + v * 20, str(round(v, 1)))

## geojson 자료 확인

연령별_거주인구 = gpd.read_file(input_path.joinpath('19.세종시_연령별_거주인구정보_격자.geojson'))
연령별_거주인구

도로명주소 = gpd.read_file(input_path.joinpath('23.세종시_도로명주소_건물.geojson'))
도로명주소

건축물연면적 = gpd.read_file(input_path.joinpath('24.세종시_건축물연면적_격자.geojson'))
건축물연면적

법정경계_시군구 = gpd.read_file(input_path.joinpath('30.세종시_법정경계(시군구).geojson'))
법정경계_시군구

법정경계_읍면동 = gpd.read_file(input_path.joinpath('31.세종시_법정경계(읍면동).geojson'))
법정경계_읍면동

행정경계_읍면동 = gpd.read_file(input_path.joinpath('32.세종시_행정경계(읍면동).geojson'))
행정경계_읍면동

지적도 = gpd.read_file(input_path.joinpath('33.세종시_지적도.geojson'))
지적도

## 지역별 상권정보

# 자료 불러오기
상권정보 = pd.read_csv(input_path.joinpath('14.세종시_상권정보.csv'))
상권정보

# 지역별 각 상점 개수와 합계
data_상권정보 = pd.crosstab(상권정보.행정동명, 상권정보.상권업종대분류명, margins=True)
data_상권정보

# 지역별 상권 수
data_상권정보_all = data_상권정보['All']
data_상권정보_all

# 지역별 위도와 경도
행정경계_읍면동 = gpd.read_file(input_path.joinpath('32.세종시_행정경계(읍면동).geojson'))
행정경계_읍면동

행정경계_읍면동['lon'] = (행정경계_읍면동['geometry'].bounds['maxx'] + 행정경계_읍면동['geometry'].bounds['minx']) / 2
행정경계_읍면동['lat'] = (행정경계_읍면동['geometry'].bounds['maxy'] + 행정경계_읍면동['geometry'].bounds['miny']) / 2
data_상권정보_lon_lat = 행정경계_읍면동[['ADM_DR_NM', 'lon', 'lat']]
data_상권정보_lon_lat = data_상권정보_lon_lat.rename(columns={'ADM_DR_NM': '행정동명'})
data_상권정보_lon_lat

# 지역별 위도와 경도, 총 상점 수 합치기
data_상권정보_info = pd.merge(data_상권정보_all, data_상권정보_lon_lat, on="행정동명")
data_상권정보_info

# 상권업종대분류명 사전순 정렬
data_상권정보 = 상권정보
data_상권정보 = data_상권정보.sort_values(by='상권업종대분류명')
data_상권정보

data_상권정보 = data_상권정보[['상권업종대분류명', '도로명주소', 'lon', 'lat']]

# 상권업종대분류명을 상권종류로 이름 변경
data_상권정보.rename(columns={'상권업종대분류명': '상권종류'}, inplace=True)
data_상권정보

# 지역 별 평균 가격 그래프
plt.figure(figsize=(15, 6))
sns.countplot(data=상권정보, x="행정동명", order=상권정보['행정동명'].value_counts().index)

## 상권 수 지도에 표시
# 위도, 경도, 총 상권 개수를 float 형으로 바꿈
data_상권정보_info['lon'] = data_상권정보_info.lon.astype(float)
data_상권정보_info['lat'] = data_상권정보_info.lat.astype(float)
data_상권정보_info['All'] = data_상권정보_info.All.astype(float)
data_상권정보_info

# 상권 수 시각화
상권수_map = folium.Map(location=[data_상권정보_info['lat'].mean(), data_상권정보_info['lon'].mean()], zoom_start=11)

for item in data_상권정보_info.index:
    latitude = data_상권정보_info.loc[item, 'lat']
longtitude = data_상권정보_info.loc[item, 'lon']
popups = folium.Popup(data_상권정보_info.loc[item, '행정동명'], max_width=100)
folium.CircleMarker([latitude, longtitude],
                    radius=data_상권정보_info.loc[item, 'All'] / 100,
                    popup=popups,
                    color='red',
                    fill=True).add_to(상권수_map)
상권수_map

## 상권 수 지도에 표시2

# 자료 불러오기
행정경계_읍면동 = gpd.read_file(input_path.joinpath('32.세종시_행정경계(읍면동).geojson'))
행정경계_읍면동

data = data_상권정보_info[['행정동명', 'All']]
data

# 지도
상권수_map2 = folium.Map(location=[data_상권정보_info['lat'].mean(), data_상권정보_info['lon'].mean()], zoom_start=11)

상권수_map2.choropleth(
    geo_data=행정경계_읍면동,
    data=data,
    columns=['행정동명', 'All'],
    key_on='feature.properties.ADM_DR_NM',
    fill_color='BuPu',
    legend_name='상권 수',
)

상권수_map2

## 상권 정보 지도에 표시
data_상권정보 = 상권정보
data_상권정보 = data_상권정보[['상권업종대분류명', '도로명주소', 'lon', 'lat']]

# 상권업종대분류명을 상권종류로 이름 변경
data_상권정보.rename(columns={'상권업종대분류명': '상권종류'}, inplace=True)
data_상권정보

# 위도, 경도 값 형 변환
data_상권정보['lon'] = data_상권정보.lon.astype(float)
data_상권정보['lat'] = data_상권정보.lat.astype(float)

# 지도

상권종류_map = folium.Map(location=[data_상권정보['lat'].mean(), data_상권정보['lon'].mean()], zoom_start=11)

for item in data_상권정보.index:
    latitude = data_상권정보.loc[item, 'lat']
longtitude = data_상권정보.loc[item, 'lon']

if data_상권정보.loc[item, '상권종류'] == '관광/여가/오락':
    colors = 'dodgerblue'

elif data_상권정보.loc[item, '상권종류'] == '부동산':
    colors = 'burlywood'

elif data_상권정보.loc[item, '상권종류'] == '생활서비스':
    colors = 'gold'

elif data_상권정보.loc[item, '상권종류'] == '소매':
    colors = 'darkolivegreen'

elif data_상권정보.loc[item, '상권종류'] == '학문/교육':
    colors = 'slategrey'

elif data_상권정보.loc[item, '상권종류'] == '음식':
    colors = 'salmon'

elif data_상권정보.loc[item, '상권종류'] == '스포츠':
    colors = 'blueviolet'

elif data_상권정보.loc[item, '상권종류'] == '숙박':
    colors = 'lihgtpink'
popups = folium.Popup(data_상권정보.loc[item, '도로명주소'], max_width=150)
folium.CircleMarker([latitude, longtitude],
                    popup=popups,
                    color=colors,
                    fill=True).add_to(상권종류_map)
상권종류_map

## 아파트 시세 지도

아파트_매매

# 법정경계에 맞게 시군구 편집

data_시군구_아파트 = 아파트_매매[['시군구', '거래금액(만원)']]
for i in range(len(data_시군구_아파트['시군구'])):
    if
len(data_시군구_아파트.loc[i, '시군구']) == 9:
data_시군구_아파트['시군구'][i] = data_시군구_아파트['시군구'][i][:5]
elif len(data_시군구_아파트.loc[i, '시군구']) == 8:

if data_시군구_아파트.loc[i, '시군구'][1] == '조':
    data_시군구_아파트['시군구'][i] = data_시군구_아파트['시군구'][i][:5]
else:
    data_시군구_아파트['시군구'][i] = data_시군구_아파트['시군구'][i][:5]

data_시군구_아파트

# 시군구별 거래금액(만원) 평균
data_시군구_아파트 = data_시군구_아파트.groupby(data_시군구_아파트.시군구)['거래금액(만원)'].mean()
data_시군구_아파트

data_시군구_아파트 = data_시군구_아파트.reset_index()
data_시군구_아파트

for i in range(len(data_시군구_아파트['시군구'])):
    data_시군구_아파트['시군구'][i] = data_시군구_아파트['시군구'][i][1:]

data_시군구_아파트

# 자료 불러오기
법정경계_시군구 = gpd.read_file(input_path.joinpath('31.세종시_법정경계(읍면동).geojson'))
법정경계_시군구

# 지역별 위도와 경도
법정경계_시군구['lon'] = (법정경계_시군구['geometry'].bounds['maxx'] + 법정경계_시군구['geometry'].bounds['minx']) / 2
법정경계_시군구['lat'] = (법정경계_시군구['geometry'].bounds['maxy'] + 법정경계_시군구['geometry'].bounds['miny']) / 2

data_아파트_lon_lat = 법정경계_시군구[['EMD_KOR_NM', 'lon', 'lat']]
data_아파트_lon_lat = data_아파트_lon_lat.rename(columns={'EMD_KOR_NM': '시군구'})
data_아파트_lon_lat

# 법정경계에 맞춰 아파트 행 추가
data_시군구_아파트.loc[len(data_시군구_아파트)] = ['가람동', 0]
data_시군구_아파트.loc[len(data_시군구_아파트)] = ['산울동', 0]
data_시군구_아파트.loc[len(data_시군구_아파트)] = ['해밀동', 0]
data_시군구_아파트.loc[len(data_시군구_아파트)] = ['합강동', 0]
data_시군구_아파트.loc[len(data_시군구_아파트)] = ['집현동', 0]
data_시군구_아파트.loc[len(data_시군구_아파트)] = ['연기면', 0]
data_시군구_아파트

data_시군구_아파트['시군구'][1] = '금남면'
data_시군구_아파트['시군구'][8] = '부강면'
data_시군구_아파트['시군구'][11] = '소정면'
data_시군구_아파트['시군구'][14] = '연동면'
data_시군구_아파트['시군구'][15] = '연서면'
data_시군구_아파트['시군구'][16] = '장군면'
data_시군구_아파트['시군구'][17] = '전동면'
data_시군구_아파트['시군구'][18] = '전의면'

data_시군구_아파트_info = pd.merge(data_아파트_lon_lat, data_시군구_아파트, on='시군구', how="outer")
data_시군구_아파트_info

# 위도, 경도를 float 형으로 바꿈
data_시군구_아파트_info['lon'] = data_시군구_아파트_info.lon.astype(float)
data_시군구_아파트_info['lat'] = data_시군구_아파트_info.lat.astype(float)

# 지도
법정경계_시군구 = gpd.read_file(input_path.joinpath('31.세종시_법정경계(읍면동).geojson'))
법정경계_시군구

아파트시세_map = folium.Map(location=[data_시군구_아파트_info['lat'].mean(), data_시군구_아파트_info['lon'].mean()], zoom_start=11)

data = data_시군구_아파트_info[['시군구', '거래금액(만원)']]

folium.Choropleth(
    geo_data=법정경계_시군구,
    data=data,
    columns=['시군구', '거래금액(만원)'],
    key_on='feature.properties.EMD_KOR_NM',
    fill_color='BuPu',
    legend_name='아파트시세',
).add_to(아파트시세_map)

아파트시세_map

## 년도별 지역 전입자수

# 자료 불러오기
전입 = pd.read_csv(input_path.joinpath('20.세종시_전입자수.csv'))
전입

# 자료 불러오기
전출 = pd.read_csv(input_path.joinpath('21.세종시_전출자수.csv'))
전출

# 지역별 총 전입자 수 구하기
data_전입자수 = 전입.groupby('세종전입행정동')['전입자수'].agg('sum')
data_전입자수

# 지역별 총 전입자 수 구하기
data_전출자수 = 전출.groupby('세종전출행정동')['전출자수'].agg('sum')
data_전출자수

# 그래프 그리기
ax = data_전입자수.plot(kind='bar', title='지역별 전입자 수', figsize=(15, 5), legend=True, fontsize=10, color='white')
ax.plot(data_전출자수, linestyle='--', color='blue')
ax.plot(data_전입자수, linestyle='--', color='red')
ax.set_xlabel('지역', fontsize=12)
ax.set_ylabel('전입자 수', fontsize=12)
ax.legend(['전입자 수'], fontsize=12)

## 지역별 지목 거래금액과 계약면적 표

# 자료 불러오기
토지 = pd.read_csv(input_path.joinpath('12.세종시_토지(매매)_실거래가.csv'), encoding='utf-8')

# 시군구 편집
for i in range(len(토지['시군구'])):
    토지['시군구'][i] = 토지['시군구'][i][8:12]
토지

# 지역별 지목의 계약 면적과 거래금액 표
pd.set_option('display.max_rows', 700)
토지['거래금액(만원)'] = 토지['거래금액(만원)'].apply(lambda x: float(x.split()[0].replace(',', '')))
data_토지 = round(토지.groupby(['시군구', '지목'])[['계약면적(㎡)', '거래금액(만원)']].mean(), 3)
data_토지 = data_토지.reset_index()
data_토지

# 시군구별 지목-금액, 지목-면적으로 표 나누기
data_토지_금액 = data_토지[['지목', '거래금액(만원)']]
data_토지_면적 = data_토지[['지목', '계약면적(㎡)']]

## 지역별 지목 거래금액과 거래면적 지도

# 31.세종시_법정경계(읍면동).geojson 에서 만든 시군구별 위도, 경도 표
지목_lon_lat = data_아파트_lon_lat
지목_lon_lat

data_토지 = data_토지.reset_index()
data_토지

# 시군구별로 지목 분리
data_고운동 = data_토지[data_토지['시군구'] == '고운동']
data_고운동 = data_고운동.set_index('지목')

data_금남면 = data_토지[data_토지['시군구'] == '금남면 ']
data_금남면 = data_금남면.set_index('지목')

data_나성동 = data_토지[data_토지['시군구'] == '나성동']
data_나성동 = data_나성동.set_index('지목')

data_다정동 = data_토지[data_토지['시군구'] == '다정동']
data_다정동 = data_다정동.set_index('지목')

data_대평동 = data_토지[data_토지['시군구'] == '대평동']
data_대평동 = data_대평동.set_index('지목')

data_도담동 = data_토지[data_토지['시군구'] == '도담동']
data_도담동 = data_도담동.set_index('지목')

data_반곡동 = data_토지[data_토지['시군구'] == '반곡동']
data_반곡동 = data_반곡동.set_index('지목')

data_보람동 = data_토지[data_토지['시군구'] == '보람동']
data_보람동 = data_보람동.set_index('지목')

data_부강면 = data_토지[data_토지['시군구'] == '부강면 ']
data_부강면 = data_부강면.set_index('지목')

data_새롬동 = data_토지[data_토지['시군구'] == '새롬동']
data_새롬동 = data_새롬동.set_index('지목')

data_소담동 = data_토지[data_토지['시군구'] == '소담동']
data_소담동 = data_소담동.set_index('지목')

data_소정면 = data_토지[data_토지['시군구'] == '소정면 ']
data_소정면 = data_소정면.set_index('지목')

data_아름동 = data_토지[data_토지['시군구'] == '아름동']
data_아름동 = data_아름동.set_index('지목')

data_어진동 = data_토지[data_토지['시군구'] == '어진동']
data_어진동 = data_어진동.set_index('지목')

data_연기면 = data_토지[data_토지['시군구'] == '연기면 ']
data_연기면 = data_연기면.set_index('지목')

data_연동면 = data_토지[data_토지['시군구'] == '연동면 ']
data_연동면 = data_연동면.set_index('지목')

data_연서면 = data_토지[data_토지['시군구'] == '연서면 ']
data_연서면 = data_연서면.set_index('지목')

data_장군면 = data_토지[data_토지['시군구'] == '장군면 ']
data_장군면 = data_장군면.set_index('지목')

data_전동면 = data_토지[data_토지['시군구'] == '전동면 ']
data_전동면 = data_전동면.set_index('지목')

data_전의면 = data_토지[data_토지['시군구'] == '전의면 ']
data_전의면 = data_전의면.set_index('지목')

data_조치원읍 = data_토지[data_토지['시군구'] == '조치원읍']
data_조치원읍 = data_조치원읍.set_index('지목')

data_집현동 = data_토지[data_토지['시군구'] == '집현동']
data_집현동 = data_집현동.set_index('지목')

data_한솔동 = data_토지[data_토지['시군구'] == '한솔동']
data_한솔동 = data_한솔동.set_index('지목')

data_해밀동 = data_토지[data_토지['시군구'] == '해밀동']
data_해밀동 = data_해밀동.set_index('지목')

# 시군구별로 분리된 표를 금액과 면적으로 나눔

고운동_금액 = Bar(data_고운동['거래금액(만원)'], width=400, height=200).axis_titles(x='지목', y='거래금액')
고운동_면적 = Bar(data_고운동['계약면적(㎡)'], width=400, height=200).axis_titles(x='지목', y='계약면적')

금남면_금액 = Bar(data_금남면['거래금액(만원)'], width=650, height=200).axis_titles(x='지목', y='거래금액')
금남면_면적 = Bar(data_금남면['계약면적(㎡)'], width=650, height=200).axis_titles(x='지목', y='계약면적')

나성동_금액 = Bar(data_나성동['거래금액(만원)'], width=10, height=200).axis_titles(x='지목', y='거래금액')
나성동_면적 = Bar(data_나성동['계약면적(㎡)'], width=100, height=200).axis_titles(x='지목', y='계약면적')

다정동_금액 = Bar(data_다정동['거래금액(만원)'], width=100, height=200).axis_titles(x='지목', y='거래금액')
다정동_면적 = Bar(data_다정동['계약면적(㎡)'], width=100, height=200).axis_titles(x='지목', y='계약면적')

대평동_금액 = Bar(data_대평동['거래금액(만원)'], width=400, height=200).axis_titles(x='지목', y='거래금액')
대평동_면적 = Bar(data_대평동['계약면적(㎡)'], width=400, height=200).axis_titles(x='지목', y='계약면적')

도담동_금액 = Bar(data_도담동['거래금액(만원)'], width=100, height=200).axis_titles(x='지목', y='거래금액')
도담동_면적 = Bar(data_도담동['계약면적(㎡)'], width=100, height=200).axis_titles(x='지목', y='계약면적')

반곡동_금액 = Bar(data_반곡동['거래금액(만원)'], width=100, height=200).axis_titles(x='지목', y='거래금액')
반곡동_면적 = Bar(data_반곡동['계약면적(㎡)'], width=100, height=200).axis_titles(x='지목', y='계약면적')

보람동_금액 = Bar(data_보람동['거래금액(만원)'], width=400, height=200).axis_titles(x='지목', y='거래금액')
보람동_면적 = Bar(data_보람동['계약면적(㎡)'], width=400, height=200).axis_titles(x='지목', y='계약면적')

부강면_금액 = Bar(data_부강면['거래금액(만원)'], width=750, height=200).axis_titles(x='지목', y='거래금액')
부강면_면적 = Bar(data_부강면['계약면적(㎡)'], width=750, height=200).axis_titles(x='지목', y='계약면적')

새롬동_금액 = Bar(data_새롬동['거래금액(만원)'], width=100, height=200).axis_titles(x='지목', y='거래금액')
새롬동_면적 = Bar(data_새롬동['계약면적(㎡)'], width=100, height=200).axis_titles(x='지목', y='계약면적')

소담동_금액 = Bar(data_소담동['거래금액(만원)'], width=400, height=200).axis_titles(x='지목', y='거래금액')
소담동_면적 = Bar(data_소담동['계약면적(㎡)'], width=400, height=200).axis_titles(x='지목', y='계약면적')

소정면_금액 = Bar(data_소정면['거래금액(만원)'], width=400, height=200).axis_titles(x='지목', y='거래금액')
소정면_면적 = Bar(data_소정면['계약면적(㎡)'], width=400, height=200).axis_titles(x='지목', y='계약면적')

아름동_금액 = Bar(data_아름동['거래금액(만원)'], width=100, height=200).axis_titles(x='지목', y='거래금액')
아름동_면적 = Bar(data_아름동['계약면적(㎡)'], width=100, height=200).axis_titles(x='지목', y='계약면적')

어진동_금액 = Bar(data_어진동['거래금액(만원)'], width=100, height=200).axis_titles(x='지목', y='거래금액')
어진동_면적 = Bar(data_어진동['계약면적(㎡)'], width=100, height=200).axis_titles(x='지목', y='계약면적')

연기면_금액 = Bar(data_연기면['거래금액(만원)'], width=500, height=200).axis_titles(x='지목', y='거래금액')
연기면_면적 = Bar(data_연기면['계약면적(㎡)'], width=500, height=200).axis_titles(x='지목', y='계약면적')

연동면_금액 = Bar(data_연동면['거래금액(만원)'], width=650, height=200).axis_titles(x='지목', y='거래금액')
연동면_면적 = Bar(data_연동면['계약면적(㎡)'], width=650, height=200).axis_titles(x='지목', y='계약면적')

연서면_금액 = Bar(data_연서면['거래금액(만원)'], width=650, height=200).axis_titles(x='지목', y='거래금액')
연서면_면적 = Bar(data_연서면['계약면적(㎡)'], width=650, height=200).axis_titles(x='지목', y='계약면적')

장군면_금액 = Bar(data_장군면['거래금액(만원)'], width=650, height=200).axis_titles(x='지목', y='거래금액')
장군면_면적 = Bar(data_장군면['계약면적(㎡)'], width=650, height=200).axis_titles(x='지목', y='계약면적')

전동면_금액 = Bar(data_전동면['거래금액(만원)'], width=650, height=200).axis_titles(x='지목', y='거래금액')
전동면_면적 = Bar(data_전동면['계약면적(㎡)'], width=650, height=200).axis_titles(x='지목', y='계약면적')

전의면_금액 = Bar(data_전의면['거래금액(만원)'], width=700, height=200).axis_titles(x='지목', y='거래금액')
전의면_면적 = Bar(data_전의면['계약면적(㎡)'], width=700, height=200).axis_titles(x='지목', y='계약면적')

조치원읍_금액 = Bar(data_조치원읍['거래금액(만원)'], width=550, height=200).axis_titles(x='지목', y='거래금액')
조치원읍_면적 = Bar(data_조치원읍['계약면적(㎡)'], width=550, height=200).axis_titles(x='지목', y='계약면적')

집현동_금액 = Bar(data_집현동['거래금액(만원)'], width=100, height=200).axis_titles(x='지목', y='거래금액')
집현동_면적 = Bar(data_집현동['계약면적(㎡)'], width=100, height=200).axis_titles(x='지목', y='계약면적')

한솔동_금액 = Bar(data_한솔동['거래금액(만원)'], width=100, height=200).axis_titles(x='지목', y='거래금액')
한솔동_면적 = Bar(data_한솔동['계약면적(㎡)'], width=100, height=200).axis_titles(x='지목', y='계약면적')

해밀동_금액 = Bar(data_해밀동['거래금액(만원)'], width=100, height=200).axis_titles(x='지목', y='거래금액')
해밀동_면적 = Bar(data_해밀동['계약면적(㎡)'], width=100, height=200).axis_titles(x='지목', y='계약면적')

# 지도

법정경계_읍면동 = gpd.read_file(input_path.joinpath('31.세종시_법정경계(읍면동).geojson'))
법정경계_읍면동

지목_map = folium.Map(location=[지목_lon_lat['lat'].mean(), 지목_lon_lat['lon'].mean()], zoom_start=11)

# 지역 구분
지목_map.choropleth(
    geo_data=법정경계_읍면동,
    key_on='feature.properties.EMD_KOR_NM',
    fill_color='White',
    fill_opacity=0.3,
    legend_name='지목 종류',
)

# 지역별 지목의 금액은 빨간원, 면적은 파란원으로 표시
for i in range(len(지목_lon_lat['시군구'])):
    latitude_금액 = 지목_lon_lat['lat'][i]
longtitude_금액 = 지목_lon_lat['lon'][i]

latitude_면적 = (지목_lon_lat['lat'][i] + 0.002)
longtitude_면적 = (지목_lon_lat['lon'][i] + 0.002)

popups_금액 = folium.Popup(지목_lon_lat['시군구'][i], max_width=100)
popups_면적 = folium.Popup(지목_lon_lat['시군구'][i], max_width=100)

if (지목_lon_lat['시군구'][i] == '고운동'):
    popups_금액 = folium.Popup(max_width=500).add_child(
        folium.Vega(고운동_금액, width=450, height=250))
popups_면적 = folium.Popup(max_width=500).add_child(
    folium.Vega(고운동_면적, width=450, height=250))

elif (지목_lon_lat['시군구'][i] == '금남면'):
popups_금액 = folium.Popup(max_width=800).add_child(
    folium.Vega(금남면_금액, width=750, height=250))
popups_면적 = folium.Popup(max_width=800).add_child(
    folium.Vega(금남면_면적, width=750, height=250))

elif (지목_lon_lat['시군구'][i] == '나성동'):
popups_금액 = folium.Popup(max_width=200).add_child(
    folium.Vega(나성동_금액, width=150, height=250))
popups_면적 = folium.Popup(max_width=200).add_child(
    folium.Vega(나성동_면적, width=150, height=250))

elif (지목_lon_lat['시군구'][i] == '다정동'):
popups_금액 = folium.Popup(max_width=200).add_child(
    folium.Vega(다정동_금액, width=150, height=250))
popups_면적 = folium.Popup(max_width=200).add_child(
    folium.Vega(다정동_면적, width=150, height=250))

elif (지목_lon_lat['시군구'][i] == '대평동'):
popups_금액 = folium.Popup(max_width=500).add_child(
    folium.Vega(대평동_금액, width=450, height=250))
popups_면적 = folium.Popup(max_width=500).add_child(
    folium.Vega(대평동_면적, width=450, height=250))

elif (지목_lon_lat['시군구'][i] == '도담동'):
popups_금액 = folium.Popup(max_width=200).add_child(
    folium.Vega(도담동_금액, width=150, height=250))
popups_면적 = folium.Popup(max_width=200).add_child(
    folium.Vega(도담동_면적, width=150, height=250))

elif (지목_lon_lat['시군구'][i] == '반곡동'):
popups_금액 = folium.Popup(max_width=200).add_child(
    folium.Vega(반곡동_금액, width=150, height=250))
popups_면적 = folium.Popup(max_width=200).add_child(
    folium.Vega(반곡동_면적, width=150, height=250))

elif (지목_lon_lat['시군구'][i] == '보람동'):
popups_금액 = folium.Popup(max_width=500).add_child(
    folium.Vega(보람동_금액, width=450, height=250))
popups_면적 = folium.Popup(max_width=500).add_child(
    folium.Vega(보람동_면적, width=450, height=250))

elif (지목_lon_lat['시군구'][i] == '부강면'):
popups_금액 = folium.Popup(max_width=850).add_child(
    folium.Vega(부강면_금액, width=800, height=250))
popups_면적 = folium.Popup(max_width=850).add_child(
    folium.Vega(부강면_면적, width=800, height=250))

elif (지목_lon_lat['시군구'][i] == '새롬동'):
popups_금액 = folium.Popup(max_width=200).add_child(
    folium.Vega(새롬동_금액, width=150, height=250))
popups_면적 = folium.Popup(max_width=200).add_child(
    folium.Vega(새롬동_면적, width=150, height=250))

elif (지목_lon_lat['시군구'][i] == '소담동'):
popups_금액 = folium.Popup(max_width=500).add_child(
    folium.Vega(소담동_금액, width=450, height=250))
popups_면적 = folium.Popup(max_width=500).add_child(
    folium.Vega(소담동_면적, width=450, height=250))

elif (지목_lon_lat['시군구'][i] == '소정면'):
popups_금액 = folium.Popup(max_width=500).add_child(
    folium.Vega(소정면_금액, width=450, height=250))
popups_면적 = folium.Popup(max_width=500).add_child(
    folium.Vega(소정면_면적, width=450, height=250))

elif (지목_lon_lat['시군구'][i] == '아름동'):
popups_금액 = folium.Popup(max_width=200).add_child(
    folium.Vega(아름동_금액, width=150, height=250))
popups_면적 = folium.Popup(max_width=200).add_child(
    folium.Vega(아름동_면적, width=150, height=250))

elif (지목_lon_lat['시군구'][i] == '어진동'):
popups_금액 = folium.Popup(max_width=200).add_child(
    folium.Vega(어진동_금액, width=150, height=250))
popups_면적 = folium.Popup(max_width=200).add_child(
    folium.Vega(어진동_면적, width=150, height=250))

elif (지목_lon_lat['시군구'][i] == '연기면'):
popups_금액 = folium.Popup(max_width=600).add_child(
    folium.Vega(연기면_금액, width=550, height=250))
popups_면적 = folium.Popup(max_width=600).add_child(
    folium.Vega(연기면_면적, width=550, height=250))

elif (지목_lon_lat['시군구'][i] == '연동면'):
popups_금액 = folium.Popup(max_width=750).add_child(
    folium.Vega(연동면_금액, width=700, height=250))
popups_면적 = folium.Popup(max_width=750).add_child(
    folium.Vega(연동면_면적, width=700, height=250))

elif (지목_lon_lat['시군구'][i] == '연서면'):
popups_금액 = folium.Popup(max_width=800).add_child(
    folium.Vega(연서면_금액, width=750, height=250))
popups_면적 = folium.Popup(max_width=800).add_child(
    folium.Vega(연서면_면적, width=750, height=250))

elif (지목_lon_lat['시군구'][i] == '장군면'):
popups_금액 = folium.Popup(max_width=800).add_child(
    folium.Vega(장군면_금액, width=750, height=250))
popups_면적 = folium.Popup(max_width=800).add_child(
    folium.Vega(장군면_면적, width=750, height=250))

elif (지목_lon_lat['시군구'][i] == '전동면'):
popups_금액 = folium.Popup(max_width=800).add_child(
    folium.Vega(전동면_금액, width=750, height=250))
popups_면적 = folium.Popup(max_width=800).add_child(
    folium.Vega(전동면_면적, width=750, height=250))

elif (지목_lon_lat['시군구'][i] == '전의면'):
popups_금액 = folium.Popup(max_width=800).add_child(
    folium.Vega(전의면_금액, width=780, height=250))
popups_면적 = folium.Popup(max_width=800).add_child(
    folium.Vega(전의면_면적, width=780, height=250))

elif (지목_lon_lat['시군구'][i] == '조치원읍'):
popups_금액 = folium.Popup(max_width=650).add_child(
    folium.Vega(조치원읍_금액, width=600, height=250))
popups_면적 = folium.Popup(max_width=650).add_child(
    folium.Vega(조치원읍_면적, width=600, height=250))

elif (지목_lon_lat['시군구'][i] == '집현동'):
popups_금액 = folium.Popup(max_width=200).add_child(
    folium.Vega(집현동_금액, width=150, height=250))
popups_면적 = folium.Popup(max_width=200).add_child(
    folium.Vega(집현동_면적, width=150, height=250))

elif (지목_lon_lat['시군구'][i] == '한솔동'):
popups_금액 = folium.Popup(max_width=200).add_child(
    folium.Vega(한솔동_금액, width=150, height=250))
popups_면적 = folium.Popup(max_width=200).add_child(
    folium.Vega(한솔동_면적, width=150, height=250))

elif (지목_lon_lat['시군구'][i] == '해밀동'):
popups_금액 = folium.Popup(max_width=200).add_child(
    folium.Vega(해밀동_금액, width=150, height=250))
popups_면적 = folium.Popup(max_width=200).add_child(
    folium.Vega(해밀동_면적, width=150, height=250))

folium.CircleMarker([latitude_금액, longtitude_금액],
                    popup=popups_금액,
                    color='crimson',
                    fill=True).add_to(지목_map)

folium.CircleMarker([latitude_면적, longtitude_면적],
                    popup=popups_면적,
                    color='midnightblue',
                    fill=True).add_to(지목_map)

지목_map

## 분양권 (시군구-단지명-분/입구분-평수 별 거래금액 표)

# 자료 불러오기
분양권 = pd.read_csv(input_path.joinpath('13.세종시_분양권_실거래가.csv'))

# 세종 특별자치시 없애기
for i in range(len(분양권['시군구'])):
    분양권['시군구'][i] = 분양권['시군구'][i][8:]

분양권

# 전용면적을 평수로 바꿈
분양권['평수'] = '평수'
분양권['평수크기'] = 0
for i in range(len(분양권['전용면적(㎡)'])):
    if
분양권['전용면적(㎡)'][i] / 3.3 < 10:
분양권['평수'][i] = '10평 미만'
분양권['평수크기'][i] = 1
elif 분양권['전용면적(㎡)'][i] / 3.3 < 20:
분양권['평수'][i] = '10평대'
분양권['평수크기'][i] = 10
elif 분양권['전용면적(㎡)'][i] / 3.3 < 30:
분양권['평수'][i] = '20평대'
분양권['평수크기'][i] = 20
elif 분양권['전용면적(㎡)'][i] / 3.3 < 40:
분양권['평수'][i] = '30평대'
분양권['평수크기'][i] = 30
elif 분양권['전용면적(㎡)'][i] / 3.3 < 50:
분양권['평수'][i] = '40평대'
분양권['평수크기'][i] = 40
elif 분양권['전용면적(㎡)'][i] / 3.3 < 60:
분양권['평수'][i] = '50평대'
분양권['평수크기'][i] = 50
elif 분양권['전용면적(㎡)'][i] / 3.3 < 70:
분양권['평수'][i] = '60평대'
분양권['평수크기'][i] = 60

분양권

# 시군구 - 단지 - 입/분 - 평수 별 평균 금액 표
분양권['거래금액(만원)'] = 분양권['거래금액(만원)'].apply(lambda x: float(x.split()[0].replace(',', '')))
data_분양권 = round(분양권.groupby(['시군구', '단지명', '분/입구분', '평수'])[['거래금액(만원)']].mean(), 3)
data_분양권

## 분양권 그래프

# 분양권['거래금액(만원)'] = 분양권['거래금액(만원)'].apply(lambda x: float(x.split()[0].replace(',','')))
data_분양권 = round(분양권.groupby(['시군구', '단지명', '분/입구분', '평수'])[['거래금액(만원)', '평수크기']].mean(), 3)
data_분양권

# 시군구별로 분리
data_분양권 = data_분양권.reset_index()
data_분양권_고운동 = data_분양권[data_분양권['시군구'] == '고운동']
data_분양권_나성동 = data_분양권[data_분양권['시군구'] == '나성동']
data_분양권_다정동 = data_분양권[data_분양권['시군구'] == '다정동']
data_분양권_대평동 = data_분양권[data_분양권['시군구'] == '대평동']
data_분양권_도담동 = data_분양권[data_분양권['시군구'] == '도담동']
data_분양권_반곡동 = data_분양권[data_분양권['시군구'] == '반곡동']
data_분양권_보람동 = data_분양권[data_분양권['시군구'] == '보람동']
data_분양권_새롬동 = data_분양권[data_분양권['시군구'] == '새롬동']
data_분양권_소담동 = data_분양권[data_분양권['시군구'] == '소담동']
data_분양권_어진동 = data_분양권[data_분양권['시군구'] == '어진동']
data_분양권_종촌동 = data_분양권[data_분양권['시군구'] == '종촌동']
data_분양권_집현동 = data_분양권[data_분양권['시군구'] == '집현동']
data_분양권_해밀동 = data_분양권[data_분양권['시군구'] == '해밀동']

# 그래프 한글깨짐 방지
import matplotlib

matplotlib.font_manager._rebuild()
plt.rc("font", family="Malgun Gothic")

# '분'은 보라, '입'은 노랑, 평수별로 동그라미 크기가 다름
고운동_scatter = plt.figure(figsize=(15, 4))
고운동_scatter = plt.xticks(rotation=45)
고운동_scatter = plt.scatter(data_분양권_고운동['단지명'], data_분양권_고운동['거래금액(만원)'], c=data_분양권_고운동['분/입구분'] == '입',
                          edgecolors='grey', linewidth=2, s=data_분양권_고운동['평수크기'] * 3, alpha=0.5)
고운동_scatter = plt.xlabel('단지명')
고운동_scatter = plt.ylabel('거래금액(만원)')
고운동_scatter = plt.title('고운동')

나성동_scatter = plt.figure(figsize=(15, 4))
나성동_scatter = plt.xticks(rotation=45)
나성동_scatter = plt.scatter(data_분양권_나성동['단지명'], data_분양권_나성동['거래금액(만원)'], c=data_분양권_나성동['분/입구분'] == '입',
                          edgecolors='grey', linewidth=2, s=data_분양권_나성동['평수크기'] * 3, alpha=0.5)
나성동_scatter = plt.xlabel('단지명')
나성동_scatter = plt.ylabel('거래금액(만원)')
나성동_scatter = plt.title('나성동')

다정동_scatter = plt.figure(figsize=(15, 4))
다정동_scatter = plt.xticks(rotation=90)
다정동_scatter = plt.scatter(data_분양권_다정동['단지명'], data_분양권_다정동['거래금액(만원)'], c=data_분양권_다정동['분/입구분'] == '입',
                          edgecolors='grey', linewidth=2, s=data_분양권_다정동['평수크기'] * 3, alpha=0.5)
다정동_scatter = plt.xlabel('단지명')
다정동_scatter = plt.ylabel('거래금액(만원)')
다정동_scatter = plt.title('다정동')

대평동_scatter = plt.figure(figsize=(15, 4))
고운동_scatter = plt.xticks(rotation=45)
대평동_scatter = plt.scatter(data_분양권_대평동['단지명'], data_분양권_대평동['거래금액(만원)'], c=data_분양권_대평동['분/입구분'] == '입',
                          edgecolors='grey', linewidth=2, s=data_분양권_대평동['평수크기'] * 3, alpha=0.5)
대평동_scatter = plt.xlabel('단지명')
대평동_scatter = plt.ylabel('거래금액(만원)')
대평동_scatter = plt.title('대평동')

도담동_scatter = plt.figure(figsize=(15, 4))
도담동_scatter = plt.scatter(data_분양권_도담동['단지명'], data_분양권_도담동['거래금액(만원)'], c=data_분양권_도담동['분/입구분'] == '입',
                          edgecolors='grey', linewidth=2, s=data_분양권_도담동['평수크기'] * 3, alpha=0.5)
도담동_scatter = plt.xlabel('단지명')
도담동_scatter = plt.ylabel('거래금액(만원)')
도담동_scatter = plt.title('도담동')

반곡동_scatter = plt.figure(figsize=(15, 4))
반곡동_scatter = plt.xticks(rotation=90)
반곡동_scatter = plt.scatter(data_분양권_반곡동['단지명'], data_분양권_반곡동['거래금액(만원)'], c=data_분양권_반곡동['분/입구분'] == '입',
                          edgecolors='grey', linewidth=2, s=data_분양권_반곡동['평수크기'] * 3, alpha=0.5)
반곡동_scatter = plt.xlabel('단지명')
반곡동_scatter = plt.ylabel('거래금액(만원)')
반곡동_scatter = plt.title('반곡동')

보람동_scatter = plt.figure(figsize=(15, 4))
보람동_scatter = plt.xticks(rotation=90)
보람동_scatter = plt.scatter(data_분양권_보람동['단지명'], data_분양권_보람동['거래금액(만원)'], c=data_분양권_보람동['분/입구분'] == '입',
                          edgecolors='grey', linewidth=2, s=data_분양권_보람동['평수크기'] * 3, alpha=0.5)
보람동_scatter = plt.xlabel('단지명')
보람동_scatter = plt.ylabel('거래금액(만원)')
보람동_scatter = plt.title('보람동')

새롬동_scatter = plt.figure(figsize=(15, 4))
새롬동_scatter = plt.xticks(rotation=90)
새롬동_scatter = plt.scatter(data_분양권_새롬동['단지명'], data_분양권_새롬동['거래금액(만원)'], c=data_분양권_새롬동['분/입구분'] == '입',
                          edgecolors='grey', linewidth=2, s=data_분양권_새롬동['평수크기'] * 3, alpha=0.5)
새롬동_scatter = plt.xlabel('단지명')
새롬동_scatter = plt.ylabel('거래금액(만원)')
새롬동_scatter = plt.title('새롬동')

소담동_scatter = plt.figure(figsize=(15, 4))
고운동_scatter = plt.xticks(rotation=45)
소담동_scatter = plt.scatter(data_분양권_소담동['단지명'], data_분양권_소담동['거래금액(만원)'], c=data_분양권_소담동['분/입구분'] == '입',
                          edgecolors='grey', linewidth=2, s=data_분양권_소담동['평수크기'] * 3, alpha=0.5)
소담동_scatter = plt.xlabel('단지명')
소담동_scatter = plt.ylabel('거래금액(만원)')
소담동_scatter = plt.title('소담동')

어진동_scatter = plt.figure(figsize=(15, 4))
어진동_scatter = plt.scatter(data_분양권_어진동['단지명'], data_분양권_어진동['거래금액(만원)'], c=data_분양권_어진동['분/입구분'] == '입',
                          edgecolors='grey', linewidth=2, s=data_분양권_어진동['평수크기'] * 3, alpha=0.5)
어진동_scatter = plt.xlabel('단지명')
어진동_scatter = plt.ylabel('거래금액(만원)')
어진동_scatter = plt.title('어진동')

종촌동_scatter = plt.figure(figsize=(15, 4))
종촌동_scatter = plt.scatter(data_분양권_종촌동['단지명'], data_분양권_종촌동['거래금액(만원)'], c=data_분양권_종촌동['분/입구분'] == '분',
                          edgecolors='grey', linewidth=2, s=data_분양권_종촌동['평수크기'] * 3, alpha=0.5)
종촌동_scatter = plt.xlabel('단지명')
종촌동_scatter = plt.ylabel('거래금액(만원)')
종촌동_scatter = plt.title('종촌동')

집현동_scatter = plt.figure(figsize=(15, 4))
집현동_scatter = plt.scatter(data_분양권_집현동['단지명'], data_분양권_집현동['거래금액(만원)'], c=data_분양권_집현동['분/입구분'] == '입',
                          edgecolors='grey', linewidth=2, s=data_분양권_집현동['평수크기'] * 3, alpha=0.5)
집현동_scatter = plt.xlabel('단지명')
집현동_scatter = plt.ylabel('거래금액(만원)')
집현동_scatter = plt.title('집현동')

해밀동_scatter = plt.figure(figsize=(15, 4))
해밀동_scatter = plt.scatter(data_분양권_해밀동['단지명'], data_분양권_해밀동['거래금액(만원)'], c=data_분양권_해밀동['분/입구분'] == '입',
                          edgecolors='grey', linewidth=2, s=data_분양권_해밀동['평수크기'] * 3, alpha=0.5)
해밀동_scatter = plt.xlabel('단지명')
해밀동_scatter = plt.ylabel('거래금액(만원)')
해밀동_scatter = plt.title('해밀동')

## 인구현황 표

# 자료 불러오기
연령별_인구 = pd.read_csv(input_path.joinpath('22.세종시_연령별_인구현황.csv'))

# 열 이름 편집
for i in range(연령별_인구.shape[1]):
    if
    (연령별_인구.columns[i] != '읍면동'):
    임시_data = 연령별_인구.columns[i][7:]
연령별_인구 = 연령별_인구.rename({연령별_인구.columns[i]: 임시_data}, axis='columns')
연령별_인구

# 행과 열 이름 뒤바꾸기
data_연령별_인구 = 연령별_인구.transpose().reset_index()[1:]
data_연령별_인구 = data_연령별_인구.rename(
    columns={'index': '나이_성별', 0: '세종특별자치시', 1: '조치원읍', 2: '연기면', 3: '연동면', 4: '부강면', 5: '금남면', 6: '장군면', 7: '연서면',
             8: '전의면', 9: '전동면', 10: '소정면', 11: '한솔동', 12: '새롬동', 13: '도담동', 14: '아름동', 15: '종촌동', 16: '고운동', 17: '소담동',
             18: '보람동', 19: '대평동', 20: '다정동'})
data_연령별_인구

# 나이_성별 / 시군구별 표
data_연령별_인구 = data_연령별_인구.groupby(['나이_성별']).sum()
data_연령별_인구 = data_연령별_인구.reset_index()
data_연령별_인구

# 성별과 나이 나누기
# 성별
data_연령별_인구['성별'] = '여자'
for i in range(13):
    data_연령별_인구['성별'][i] = '남자'

# 나이
for i in range(len(data_연령별_인구['성별'])):
    data_연령별_인구['나이_성별'][i] = data_연령별_인구['나이_성별'][i][3:]
data_연령별_인구['나이_성별'][i] = data_연령별_인구['나이_성별'][i][:-1]

data_연령별_인구 = data_연령별_인구.rename(columns={'나이_성별': '나이분류'})

data_연령별_인구

data_연령별_인구['나이대'] = 0
for i in range(len(data_연령별_인구['성별'])):
    print(data_연령별_인구['나이분류'][i])
if (data_연령별_인구['나이분류'][i] == '0~9세'):
    data_연령별_인구['나이대'][i] = 1
elif (data_연령별_인구['나이분류'][i] == '10~19세'):
    data_연령별_인구['나이대'][i] = 10
elif (data_연령별_인구['나이분류'][i] == '20~29세'):
    data_연령별_인구['나이대'][i] = 20
elif (data_연령별_인구['나이분류'][i] == '30~39세'):
    data_연령별_인구['나이대'][i] = 30
elif (data_연령별_인구['나이분류'][i] == '40~49세'):
    data_연령별_인구['나이대'][i] = 40
elif (data_연령별_인구['나이분류'][i] == '50~59세'):
    data_연령별_인구['나이대'][i] = 50
elif (data_연령별_인구['나이분류'][i] == '60~69세'):
    data_연령별_인구['나이대'][i] = 60
elif (data_연령별_인구['나이분류'][i] == '70~79세'):
    data_연령별_인구['나이대'][i] = 70
elif (data_연령별_인구['나이분류'][i] == '80~89세'):
    data_연령별_인구['나이대'][i] = 80
elif (data_연령별_인구['나이분류'][i] == '90~99세'):
    data_연령별_인구['나이대'][i] = 90
elif (data_연령별_인구['나이분류'][i] == '100세_이상'):
    data_연령별_인구['나이대'][i] = 100
data_연령별_인구

# 열 순서 바꾸기
data_연령별_인구 = data_연령별_인구[['성별', '나이분류', '나이대', '세종특별자치시', '조치원읍', '연기면', '연동면', '부강면', '금남면', '장군면', '연서면',
                           '전의면', '전동면', '소정면', '한솔동', '새롬동', '도담동', '아름동', '종촌동', '고운동', '소담동',
                           '보람동', '대평동', '다정동']]
data_연령별_인구

## 인구현황 그래프

# 연령구간인구수와 총_거주자_수 삭제
data_연령별_인구 = data_연령별_인구.drop(index=[11, 12, 24, 25], axis=0)
data_연령별_인구

# 인덱스 재설정
data_연령별_인구 = data_연령별_인구.reset_index()
data_연령별_인구

# 나이대와 지역만 남기기
data_연령별_인구 = data_연령별_인구[
    ['나이대', '조치원읍', '연기면', '연동면', '부강면', '금남면', '장군면', '연서면', '전의면', '전동면', '소정면', '한솔동', '새롬동', '도담동', '아름동', '종촌동',
     '고운동', '소담동', '보람동', '대평동', '다정동']]
data_연령별_인구

# 남자 나이대-동네별 인구
data_지역별_인구_남자 = data_연령별_인구[:11]
data_지역별_인구_남자 = data_지역별_인구_남자.transpose()
data_지역별_인구_남자 = data_지역별_인구_남자[1:].reset_index()

data_지역별_인구_남자 = data_지역별_인구_남자.rename(
    columns={'index': '지역', 0: 1, 1: 100, 2: 10, 3: 20, 4: 30, 5: 40, 6: 50, 7: 60, 8: 70, 9: 80, 10: 90})
data_지역별_인구_남자 = data_지역별_인구_남자[[1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]]
data_지역별_인구_남자

# 여자 나이대-동네별 인구
data_지역별_인구_여자 = data_연령별_인구[11:]
data_지역별_인구_여자 = data_지역별_인구_여자.transpose()
data_지역별_인구_여자 = data_지역별_인구_여자[1:].reset_index()

data_지역별_인구_여자 = data_지역별_인구_여자.rename(
    columns={'index': '지역', 11: 1, 12: 100, 13: 10, 14: 20, 15: 30, 16: 40, 17: 50, 18: 60, 19: 70, 20: 80, 21: 90})
data_지역별_인구_여자 = data_지역별_인구_여자[[1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]]
data_지역별_인구_여자

# (남)나이-지역 그래프
style.use('seaborn-talk')
fig = plt.figure(figsize=(70, 23))
ax = fig.add_subplot(111, projection='3d')

# x : 나이 / y : 지역 / z : 인구 수
j = 0
colors = ['lightcoral', 'tomato', 'sandybrown', 'moccasin', 'burlywood', 'khaki', 'yellowgreen', 'lightgreen',
          'paleturquoise', 'skyblue', 'royalblue', 'slateblue', 'mediumpurple', 'plum', 'pink', 'violet', 'blueviolet',
          'slategrey', 'darkslategray', 'navy']
address = ['조치원읍', '연기면', '연동면', '부강면', '금남면', '장군면', '연서면', '전의면', '전동면', '소정면', '한솔동', '새롬동', '도담동', '아름동', '종촌동',
           '고운동', '소담동', '보람동', '대평동', '다정동']
ages = ['10살_미만', '10대', '20대', '30대', '40대', '50대', '60대', '70대', '80대', '90대', '10세_이상']
age = [1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

for c, r in zip(colors, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]):
    indexs = age
tmp = data_지역별_인구_남자.iloc[j]
tmp = tmp.reset_index()
# print(tmp)
tmp = np.array(tmp[j].tolist())
# tmp
heights = tmp
# print( r, indexs, heights, c)
ax.plot(indexs, heights, zs=r, zdir='y', color=c, alpha=0.7, marker='o')
j = j + 1

ax.set_yticklabels(address, fontsize=17, rotation=-20)
# ax.set_yticklabels(['조치원읍', '연기면', '연동면', '부강면', '금남면', '장군면', '연서면','전의면', '전동면', '소정면', '한솔동', '새롬동', '도담동', '아름동', '종촌동', '고운동', '소담동','보람동', '대평동', '다정동'])
ax.set_yticks(np.arange(0, 20, 1))
ax.set_xticks(np.arange(0, 110, 10))
ax.set_xticklabels(ages, rotation=45, fontsize=23)
ax.set_ylabel('지역')
ax.set_xlabel('나이')
ax.set_zlabel('인구수')

# (여)나이-지역 그래프
style.use('seaborn-talk')
fig = plt.figure(figsize=(70, 23))
ax = fig.add_subplot(111, projection='3d')

# x : 나이 / y : 지역 / z : 인구 수
j = 0
colors = ['lightcoral', 'tomato', 'sandybrown', 'moccasin', 'burlywood', 'khaki', 'yellowgreen', 'lightgreen',
          'paleturquoise', 'skyblue', 'royalblue', 'slateblue', 'mediumpurple', 'plum', 'pink', 'violet', 'blueviolet',
          'slategrey', 'darkslategray', 'navy']
address = ['조치원읍', '연기면', '연동면', '부강면', '금남면', '장군면', '연서면', '전의면', '전동면', '소정면', '한솔동', '새롬동', '도담동', '아름동', '종촌동',
           '고운동', '소담동', '보람동', '대평동', '다정동']
ages = ['10살_미만', '10대', '20대', '30대', '40대', '50대', '60대', '70대', '80대', '90대', '10세_이상']
age = [1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

for c, r in zip(colors, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]):
    indexs = age
tmp = data_지역별_인구_여자.iloc[j]
tmp = tmp.reset_index()
# print(tmp)
tmp = np.array(tmp[j].tolist())
# tmp
heights = tmp
# print( r, indexs, heights, c)
ax.plot(indexs, heights, zs=r, zdir='y', color=c, alpha=0.7, marker='o')
j = j + 1

ax.set_yticklabels(address, fontsize=17, rotation=-20)
ax.set_yticks(np.arange(0, 20, 1))
ax.set_xticks(np.arange(0, 110, 10))
ax.set_xticklabels(ages, rotation=45, fontsize=23)
ax.set_ylabel('지역')
ax.set_xlabel('나이')
ax.set_zlabel('인구수')

## 지역별 세대원수별 세대수 그래프

# 자료 불러오기
지역별_세대수 = pd.read_csv(input_path.joinpath('28.세종시_지역별_세대원수별_세대수.csv'))
지역별_세대수

# 세대 수만 가져오기
data_지역별_세대수 = 지역별_세대수[['1인', '2인', '3인', '4인', '5인', '6인', '7인', '8인', '9인',
                        '10인이상']]
data_지역별_세대수

# 지역별 세대원수별 세대수 그래프
style.use('seaborn-talk')
fig = plt.figure(figsize=(70, 23))
ax = fig.add_subplot(111, projection='3d')

# x : 세대원수 / y : 지역 / z : 세대 수
j = 0
colors = ['lightcoral', 'tomato', 'sandybrown', 'moccasin', 'burlywood', 'khaki', 'yellowgreen', 'lightgreen',
          'paleturquoise', 'skyblue', 'royalblue', 'slateblue', 'mediumpurple', 'plum', 'pink', 'violet', 'blueviolet',
          'slategrey', 'darkslategray']
address = ['조치원읍', '연기면', '연동면', '부강면', '금남면', '장군면', '연서면', '전의면', '전동면', '소정면', '한솔동', '새롬동', '도담동', '아름동', '종촌동',
           '고운동', '소담동', '보람동', '대평동']
populations = ['1인', '2인', '3인', '4인', '5인', '6인', '7인', '8인', '9인', '10인 이상']
population = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

for c, r in zip(colors, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]):
    indexs = population
tmp = data_지역별_세대수.iloc[j]
tmp = tmp.reset_index()
tmp = np.array(tmp[j].tolist())
heights = tmp
ax.plot(indexs, heights, zs=r, zdir='y', color=c, alpha=0.7, marker='o')
j = j + 1

ax.set_yticks(np.arange(0, 19, 1))
ax.set_yticklabels(address, fontsize=17, rotation=-20)
ax.set_xticks(np.arange(1, 11, 1))
ax.set_xticklabels(populations, rotation=45, fontsize=23)
ax.set_ylabel('지역')
ax.set_xlabel('세대원수')
ax.set_zlabel('세대수')

## 지역별 총 세대 수 그래프

# 지역 별 평균 가격 그래프
plt.figure(figsize=(20, 6))
plt.bar(지역별_세대수['읍면동'], 지역별_세대수['계'], color='lightcoral')
plt.xticks(rotation=90, fontsize=13)
plt.legend(['세대수'])
plt.title('지역별 세대수')

## 월평균 가구 소득과 소비지출액 그래프

# 자료 불러오기
가구소득 = pd.read_csv(input_path.joinpath('27.세종시_월평균_가구소득.csv'))
가구소득 = 가구소득.replace('-', 0)
가구소득

# 자료 불러오기
소비지출액 = pd.read_csv(input_path.joinpath('25.세종시_가구_월평균_소비지출액.csv'))
소비지출액

# 중분류, 소분류 제거
data_가구소득_읍면동 = 가구소득.iloc[1:4, 2:]
data_가구소득_성별 = 가구소득.iloc[4:6, 2:]
data_가구소득_거주기간 = 가구소득.iloc[6:8, 2:]
data_가구소득_연령 = 가구소득.iloc[8:15, 2:]
data_가구소득_교육정도 = 가구소득.iloc[15:19, 2:]
data_가구소득_직업 = 가구소득.iloc[19:25, 2:]
data_가구소득_혼인상태 = 가구소득.iloc[25:28, 2:]
data_가구소득_맞벌이여부 = 가구소득.iloc[28:30, 2:]
data_가구소득_주거점유형태 = 가구소득.iloc[30:33, 2:]

data_소비지출액_읍면동 = 소비지출액.iloc[1:4, 2:]
data_소비지출액_성별 = 소비지출액.iloc[4:6, 2:]
data_소비지출액_거주기간 = 소비지출액.iloc[6:8, 2:]
data_소비지출액_연령 = 소비지출액.iloc[8:15, 2:]
data_소비지출액_교육정도 = 소비지출액.iloc[15:19, 2:]
data_소비지출액_직업 = 소비지출액.iloc[19:25, 2:]
data_소비지출액_혼인상태 = 소비지출액.iloc[25:28, 2:]
data_소비지출액_가구소득 = 소비지출액.iloc[28:36, 2:]
data_소비지출액_맞벌이여부 = 소비지출액.iloc[36:38, 2:]
data_소비지출액_주거점유형태 = 소비지출액.iloc[38:41, 2:]

# str->int type으로 바꾸기
data_가구소득_읍면동 = data_가구소득_읍면동.astype(float)
data_가구소득_성별 = data_가구소득_성별.astype(float)
data_가구소득_거주기간 = data_가구소득_거주기간.astype(float)
data_가구소득_연령 = data_가구소득_연령.astype(float)
data_가구소득_교육정도 = data_가구소득_교육정도.astype(float)
data_가구소득_직업 = data_가구소득_직업.astype(float)
data_가구소득_혼인상태 = data_가구소득_혼인상태.astype(float)
data_가구소득_맞벌이여부 = data_가구소득_맞벌이여부.astype(float)
data_가구소득_주거점유형태 = data_가구소득_주거점유형태.astype(float)

data_소비지출액_읍면동 = data_소비지출액_읍면동.astype(float)
data_소비지출액_성별 = data_소비지출액_성별.astype(float)
data_소비지출액_거주기간 = data_소비지출액_거주기간.astype(float)
data_소비지출액_연령 = data_소비지출액_연령.astype(float)
data_소비지출액_교육정도 = data_소비지출액_교육정도.astype(float)
data_소비지출액_직업 = data_소비지출액_직업.astype(float)
data_소비지출액_혼인상태 = data_소비지출액_혼인상태.astype(float)
data_소비지출액_가구소득 = data_소비지출액_가구소득.astype(float)
data_소비지출액_맞벌이여부 = data_소비지출액_맞벌이여부.astype(float)
data_소비지출액_주거점유형태 = data_소비지출액_주거점유형태.astype(float)

# 그래프

fig, axes = plt.subplots(9, 2, constrained_layout=True, sharey=True)
fig.subplots_adjust(top=8, wspace=1)
# fig.suptitle('성별 월평균 가구소득과 소비지출액', fontsize=16, fontweight='bold')

# 소득 그래프
읍면동_소득_graph = data_가구소득_읍면동.plot.bar(ax=axes[0][0], fontsize=15, stacked=True, rot=0,
                                      color=['crimson', 'coral', 'lemonchiffon', 'chartreuse', 'deepskyblue',
                                             'midnightblue', 'darkviolet', 'hotpink'])
읍면동_소득_graph.set_xticklabels(['조치원읍', '면지역', '동지역'])
읍면동_소득_graph.set_title('읍면동별 월평균 가구소득', fontsize=20)
읍면동_소득_graph.legend(loc='center left', bbox_to_anchor=(1, 0.5))
for p in 읍면동_소득_graph.patches:
    x, y, width, height = p.get_bbox().bounds
if height == 0.0:
    continue
읍면동_소득_graph.text(x + width, y + height / 2, "%.1f %%" % (height), va='center', fontsize=12)

# 지출 그래프
읍면동_지출_graph = data_소비지출액_읍면동.plot.bar(ax=axes[0][1], fontsize=15, stacked=True, rot=0,
                                       color=['lightpink', 'crimson', 'coral', 'lemonchiffon', 'chartreuse',
                                              'deepskyblue', 'midnightblue', 'darkviolet'])
읍면동_지출_graph.set_xticklabels(['조치원읍', '면지역', '동지역'])
읍면동_지출_graph.set_title('읍면동별 월평균 소비지출액', fontsize=20)
읍면동_지출_graph.legend(loc='center left', bbox_to_anchor=(1, 0.5))
for p in 읍면동_지출_graph.patches:
    x, y, width, height = p.get_bbox().bounds
    if height == 0.0:
        continue
    읍면동_지출_graph.text(x + width, y + height / 2, "%.1f %%" % (height), va='center', fontsize=10)

# 소득 그래프
성별_소득_graph = data_가구소득_성별.plot.bar(ax=axes[1][0], stacked=True, rot=0, fontsize=15,
                                    color=['crimson', 'coral', 'lemonchiffon', 'chartreuse', 'deepskyblue',
                                           'midnightblue', 'darkviolet', 'hotpink'])
# 성별_소득_graph = 성별_graph.add_subplot(2, 2, 1)
성별_소득_graph.set_xticklabels(['남성', '여성'])
성별_소득_graph.set_title('성별 월평균 가구소득', fontsize=20)
성별_소득_graph.legend(loc='center left', bbox_to_anchor=(1, 0.5))
for p in 성별_소득_graph.patches:
    x, y, width, height = p.get_bbox().bounds
    if height == 0.0:
        continue
    성별_소득_graph.text(x + width, y + height / 2, "%.1f %%" % (height), va='center', ha='center', fontsize=12)

# 지출 그래프
성별_지출_graph = data_소비지출액_성별.plot.bar(ax=axes[1][1], stacked=True, rot=0, fontsize=15,
                                     color=['lightpink', 'crimson', 'coral', 'lemonchiffon', 'chartreuse',
                                            'deepskyblue', 'midnightblue', 'darkviolet'])
성별_지출_graph.set_xticklabels(['남성', '여성'])
성별_지출_graph.set_title('성별 월평균 소비지출액', fontsize=20)
성별_지출_graph.legend(loc='center left', bbox_to_anchor=(1, 0.5))
for p in 성별_지출_graph.patches:
    x, y, width, height = p.get_bbox().bounds
    if height == 0.0:
        continue
    성별_지출_graph.text(x + width, y + height / 2, "%.1f %%" % (height), va='center', fontsize=12)

# 소득 그래프
거주기간_소득_graph = data_가구소득_거주기간.plot.bar(ax=axes[2][0], fontsize=15, stacked=True, rot=0,
                                        color=['crimson', 'coral', 'lemonchiffon', 'chartreuse', 'deepskyblue',
                                               'midnightblue', 'darkviolet', 'hotpink'])
거주기간_소득_graph.set_xticklabels(['출범이전', '출범이후'])
거주기간_소득_graph.set_title('거주기간별 월평균 가구소득', fontsize=20)
거주기간_소득_graph.legend(loc='center left', bbox_to_anchor=(1, 0.5))
for p in 거주기간_소득_graph.patches:
    x, y, width, height = p.get_bbox().bounds
    if height == 0.0:
        continue
    거주기간_소득_graph.text(x + width, y + height / 2, "%.1f %%" % (height), va='center', fontsize=12)

# 지출 그래프
거주기간_지출_graph = data_소비지출액_거주기간.plot.bar(ax=axes[2][1], fontsize=15, stacked=True, rot=0,
                                         color=['lightpink', 'crimson', 'coral', 'lemonchiffon', 'chartreuse',
                                                'deepskyblue', 'midnightblue', 'darkviolet'])
거주기간_지출_graph.set_xticklabels(['출범이전', '출범이후'])
거주기간_지출_graph.set_title('거주기간별 월평균 소비지출액', fontsize=20)
거주기간_지출_graph.legend(loc='center left', bbox_to_anchor=(1, 0.5))
for p in 거주기간_지출_graph.patches:
    x, y, width, height = p.get_bbox().bounds
    if height == 0.0:
        continue
    거주기간_지출_graph.text(x + width, y + height / 2, "%.1f %%" % (height), va='center', fontsize=12)

# 소득 그래프
연령_소득_graph = data_가구소득_연령.plot.bar(ax=axes[3][0], fontsize=15, stacked=True, rot=0,
                                    color=['crimson', 'coral', 'lemonchiffon', 'chartreuse', 'deepskyblue',
                                           'midnightblue', 'darkviolet', 'hotpink'])
연령_소득_graph.set_xticklabels(['13-19세', '20-29세', '30-39세', '40-49세', '50-59세', '60세이상', '65세이상'], rotation=45)
연령_소득_graph.set_title('연령_소득별 월평균 가구소득', fontsize=20)
연령_소득_graph.legend(loc='center left', bbox_to_anchor=(1, 0.5))
for p in 연령_소득_graph.patches:
    x, y, width, height = p.get_bbox().bounds
    if height == 0.0:
        continue
    연령_소득_graph.text(x + width, y + height / 2, "%.1f %%" % (height), va='center', fontsize=8)

# 지출 그래프
연령_지출_graph = data_소비지출액_연령.plot.bar(ax=axes[3][1], fontsize=15, stacked=True, rot=0,
                                     color=['lightpink', 'crimson', 'coral', 'lemonchiffon', 'chartreuse',
                                            'deepskyblue', 'midnightblue', 'darkviolet'])
연령_지출_graph.set_xticklabels(['13-19세', '20-29세', '30-39세', '40-49세', '50-59세', '60세이상', '65세이상'], rotation=45)
연령_지출_graph.set_title('연령_소득별 월평균 소비지출액', fontsize=20)
연령_지출_graph.legend(loc='center left', bbox_to_anchor=(1, 0.5))
for p in 연령_지출_graph.patches:
    x, y, width, height = p.get_bbox().bounds
    if height == 0.0:
        continue
    연령_지출_graph.text(x + width, y + height / 2, "%.1f %%" % (height), va='center', fontsize=8)

# 소득 그래프
교육정도_소득_graph = data_가구소득_교육정도.plot.bar(ax=axes[4][0], fontsize=15, stacked=True, rot=0,
                                        color=['crimson', 'coral', 'lemonchiffon', 'chartreuse', 'deepskyblue',
                                               'midnightblue', 'darkviolet', 'hotpink'])
교육정도_소득_graph.set_xticklabels(['초졸이하', '중졸', '고졸', '대학이상'])
교육정도_소득_graph.set_title('교육정도별 월평균 가구소득', fontsize=20)
교육정도_소득_graph.legend(loc='center left', bbox_to_anchor=(1, 0.5))
for p in 교육정도_소득_graph.patches:
    x, y, width, height = p.get_bbox().bounds
    if height == 0.0:
        continue
    교육정도_소득_graph.text(x + width, y + height / 2, "%.1f %%" % (height), va='center', fontsize=12)

# 지출 그래프
교육정도_지출_graph = data_소비지출액_교육정도.plot.bar(ax=axes[4][1], fontsize=15, stacked=True, rot=0,
                                         color=['lightpink', 'crimson', 'coral', 'lemonchiffon', 'chartreuse',
                                                'deepskyblue', 'midnightblue', 'darkviolet'])
교육정도_지출_graph.set_xticklabels(['초졸이하', '중졸', '고졸', '대학이상'])
교육정도_지출_graph.set_title('교육정도별 월평균 소비지출액', fontsize=20)
교육정도_지출_graph.legend(loc='center left', bbox_to_anchor=(1, 0.5))
for p in 교육정도_지출_graph.patches:
    x, y, width, height = p.get_bbox().bounds
    if height == 0.0:
        continue
    교육정도_지출_graph.text(x + width, y + height / 2, "%.1f %%" % (height), va='center', fontsize=12)

# 소득 그래프
직업_소득_graph = data_가구소득_직업.plot.bar(ax=axes[5][0], fontsize=15, stacked=True, rot=0,
                                    color=['crimson', 'coral', 'lemonchiffon', 'chartreuse', 'deepskyblue',
                                           'midnightblue', 'darkviolet', 'hotpink'])
직업_소득_graph.set_xticklabels(['전문관리', '사무', '서비스판매', '농어업', '기능노무', '군인/주부/학생/무직'], rotation=20)
직업_소득_graph.set_title('직업_소득별 월평균 가구소득', fontsize=20)
직업_소득_graph.legend(loc='center left', bbox_to_anchor=(1, 0.5))
for p in 직업_소득_graph.patches:
    x, y, width, height = p.get_bbox().bounds
    if height == 0.0:
        continue
    직업_소득_graph.text(x + width, y + height / 2, "%.1f %%" % (height), va='center', fontsize=10)

# 지출 그래프
직업_지출_graph = data_소비지출액_직업.plot.bar(ax=axes[5][1], fontsize=15, stacked=True, rot=0,
                                     color=['lightpink', 'crimson', 'coral', 'lemonchiffon', 'chartreuse',
                                            'deepskyblue', 'midnightblue', 'darkviolet'])
직업_지출_graph.set_xticklabels(['전문관리', '사무', '서비스판매', '농어업', '기능노무', '군인/주부/학생/무직'], rotation=20)
직업_지출_graph.set_title('직업_소득별 월평균 소비지출액', fontsize=20)
직업_지출_graph.legend(loc='center left', bbox_to_anchor=(1, 0.5))
for p in 직업_지출_graph.patches:
    x, y, width, height = p.get_bbox().bounds
    if height == 0.0:
        continue
    직업_지출_graph.text(x + width, y + height / 2, "%.1f %%" % (height), va='center', fontsize=10)

# 소득 그래프
혼인상태_소득_graph = data_가구소득_혼인상태.plot.bar(ax=axes[6][0], fontsize=15, stacked=True, rot=0,
                                        color=['crimson', 'coral', 'lemonchiffon', 'chartreuse', 'deepskyblue',
                                               'midnightblue', 'darkviolet', 'hotpink'])
혼인상태_소득_graph.set_xticklabels(['미혼', '유배우', '사별/이혼'])
혼인상태_소득_graph.set_title('혼인상태별 월평균 가구소득', fontsize=20)
혼인상태_소득_graph.legend(loc='center left', bbox_to_anchor=(1, 0.5))
for p in 혼인상태_소득_graph.patches:
    x, y, width, height = p.get_bbox().bounds
    if height == 0.0:
        continue
    혼인상태_소득_graph.text(x + width, y + height / 2, "%.1f %%" % (height), va='center', fontsize=10)

# 지출 그래프
혼인상태_지출_graph = data_소비지출액_혼인상태.plot.bar(ax=axes[6][1], fontsize=15, stacked=True, rot=0,
                                         color=['lightpink', 'crimson', 'coral', 'lemonchiffon', 'chartreuse',
                                                'deepskyblue', 'midnightblue', 'darkviolet'])
혼인상태_지출_graph.set_xticklabels(['미혼', '유배우', '사별/이혼'])
혼인상태_지출_graph.set_title('혼인상태별 월평균 소비지출액', fontsize=20)
혼인상태_지출_graph.legend(loc='center left', bbox_to_anchor=(1, 0.5))
for p in 혼인상태_지출_graph.patches:
    x, y, width, height = p.get_bbox().bounds
    if height == 0.0:
        continue
    혼인상태_지출_graph.text(x + width, y + height / 2, "%.1f %%" % (height), va='center', fontsize=10)

# 소득 그래프
맞벌이여부_소득_graph = data_가구소득_맞벌이여부.plot.bar(ax=axes[7][0], fontsize=15, stacked=True, rot=0,
                                          color=['crimson', 'coral', 'lemonchiffon', 'chartreuse', 'deepskyblue',
                                                 'midnightblue', 'darkviolet', 'hotpink'])
맞벌이여부_소득_graph.set_xticklabels(['맞벌이', '맞벌이안함'])
맞벌이여부_소득_graph.set_title('맞벌이여부별 월평균 가구소득', fontsize=20)
맞벌이여부_소득_graph.legend(loc='center left', bbox_to_anchor=(1, 0.5))
for p in 맞벌이여부_소득_graph.patches:
    x, y, width, height = p.get_bbox().bounds
    if height == 0.0:
        continue
    맞벌이여부_소득_graph.text(x + width, y + height / 2, "%.1f %%" % (height), va='center', fontsize=12)

# 지출 그래프
맞벌이여부_지출_graph = data_소비지출액_맞벌이여부.plot.bar(ax=axes[7][1], fontsize=15, stacked=True, rot=0,
                                           color=['lightpink', 'crimson', 'coral', 'lemonchiffon', 'chartreuse',
                                                  'deepskyblue', 'midnightblue', 'darkviolet'])
맞벌이여부_지출_graph.set_xticklabels(['맞벌이', '맞벌이안함'])
맞벌이여부_지출_graph.set_title('맞벌이여부별 월평균 소비지출액', fontsize=20)
맞벌이여부_지출_graph.legend(loc='center left', bbox_to_anchor=(1, 0.5))
for p in 맞벌이여부_지출_graph.patches:
    x, y, width, height = p.get_bbox().bounds
    if height == 0.0:
        continue
    맞벌이여부_지출_graph.text(x + width, y + height / 2, "%.1f %%" % (height), va='center', fontsize=12)

# 소득 그래프
주거점유형태_소득_graph = data_가구소득_주거점유형태.plot.bar(ax=axes[8][0], fontsize=15, stacked=True, rot=0,
                                            color=['crimson', 'coral', 'lemonchiffon', 'chartreuse', 'deepskyblue',
                                                   'midnightblue', 'darkviolet', 'hotpink'])
주거점유형태_소득_graph.set_xticklabels(['자가집', '전세', '월세/기타'])
주거점유형태_소득_graph.set_title('주거점유형태별 월평균 가구소득', fontsize=20)
주거점유형태_소득_graph.legend(loc='center left', bbox_to_anchor=(1, 0.5))
for p in 주거점유형태_소득_graph.patches:
    x, y, width, height = p.get_bbox().bounds
    if height == 0.0:
        continue
    주거점유형태_소득_graph.text(x + width, y + height / 2, "%.1f %%" % (height), va='center', fontsize=12)

# 지출 그래프
주거점유형태_지출_graph = data_소비지출액_주거점유형태.plot.bar(ax=axes[8][1], fontsize=15, stacked=True, rot=0,
                                             color=['lightpink', 'crimson', 'coral', 'lemonchiffon', 'chartreuse',
                                                    'deepskyblue', 'midnightblue', 'darkviolet'])
주거점유형태_지출_graph.set_xticklabels(['자가집', '전세', '월세/기타'])
주거점유형태_지출_graph.set_title('주거점유형태별 월평균 소비지출액', fontsize=20)
주거점유형태_지출_graph.legend(loc='center left', bbox_to_anchor=(1, 0.5))
for p in 주거점유형태_지출_graph.patches:
    x, y, width, height = p.get_bbox().bounds
    if height == 0.0:
        continue

    주거점유형태_지출_graph.text(x + width, y + height / 2, "%.1f %%" % (height), va='center', fontsize=12)

# 지출 그래프
가구소득_소득_graph = plt.rcParams["figure.figsize"] = (15, 10)
fig.subplots_adjust(top=1.3, wspace=0.3)
가구소득_지출_graph = data_소비지출액_가구소득.plot.bar(stacked=True, rot=0,
                                         color=['lightpink', 'crimson', 'coral', 'lemonchiffon', 'chartreuse',
                                                'deepskyblue', 'midnightblue', 'darkviolet'])
가구소득_지출_graph.set_xticklabels(
    ['100만원 미만', '100~200만원 미만', '200~300만원 미만', '300~400만원 미만', '400~500만원 미만', '500~600만원 미만', '600~700만원 미만',
     '700만원 이상'])
가구소득_지출_graph.set_title('월평균 소비지출액')
가구소득_지출_graph.legend(loc='center left', bbox_to_anchor=(1, 0.5))
for p in 가구소득_지출_graph.patches:
    x, y, width, height = p.get_bbox().bounds
    if height == 0.0:
        continue
    가구소득_지출_graph.text(x + width, y + height / 2, "%.1f %%" % (height), va='center')

## 거주의사와 거주기간 그래프

# 자료 불러오기
거주의사 = pd.read_csv(input_path.joinpath('29.세종시_거주의사(향후).csv'))
거주의사

# 자료 불러오기
거주기간 = pd.read_csv(input_path.joinpath('26.세종시_거주기간.csv'))
거주기간

# 중분류, 소분류 제거
data_거주의사_읍면동 = 거주의사.iloc[1:4, 2:]
data_거주의사_성별 = 거주의사.iloc[4:6, 2:]
data_거주의사_거주기간 = 거주의사.iloc[6:8, 2:]
data_거주의사_연령 = 거주의사.iloc[8:15, 2:]
data_거주의사_교육정도 = 거주의사.iloc[15:19, 2:]
data_거주의사_직업 = 거주의사.iloc[19:25, 2:]
data_거주의사_혼인상태 = 거주의사.iloc[25:28, 2:]
data_거주의사_가구소득 = 거주의사.iloc[28:36, 2:]
data_거주의사_맞벌이 = 거주의사.iloc[36:38, 2:]
data_거주의사_주거점유형태 = 거주의사.iloc[38:41, 2:]

data_거주기간_읍면동 = 거주기간.iloc[1:4, 2:]
data_거주기간_성별 = 거주기간.iloc[4:6, 2:]
data_거주기간_연령 = 거주기간.iloc[6:13, 2:]
data_거주기간_교육정도 = 거주기간.iloc[13:17, 2:]
data_거주기간_직업 = 거주기간.iloc[17:23, 2:]
data_거주기간_혼인상태 = 거주기간.iloc[23:26, 2:]
data_거주기간_가구소득 = 거주기간.iloc[26:34, 2:]
data_거주기간_맞벌이 = 거주기간.iloc[34:36, 2:]
data_거주기간_주거점유형태 = 거주기간.iloc[36:39, 2:]

# str->int type으로 바꾸기
data_거주의사_읍면동 = data_거주의사_읍면동.astype(float)
data_거주의사_성별 = data_거주의사_성별.astype(float)
data_거주의사_거주기간 = data_거주의사_거주기간.astype(float)
data_거주의사_연령 = data_거주의사_연령.astype(float)
data_거주의사_교육정도 = data_거주의사_교육정도.astype(float)
data_거주의사_직업 = data_거주의사_직업.astype(float)
data_거주의사_혼인상태 = data_거주의사_혼인상태.astype(float)
data_거주의사_가구소득 = data_거주의사_가구소득.astype(float)
data_거주의사_맞벌이 = data_거주의사_맞벌이.astype(float)
data_거주의사_주거점유형태 = data_거주의사_주거점유형태.astype(float)

data_거주기간_읍면동 = data_거주기간_읍면동.astype(float)
data_거주기간_성별 = data_거주기간_성별.astype(float)
data_거주기간_연령 = data_거주기간_연령.astype(float)
data_거주기간_교육정도 = data_거주기간_교육정도.astype(float)
data_거주기간_직업 = data_거주기간_직업.astype(float)
data_거주기간_혼인상태 = data_거주기간_혼인상태.astype(float)
data_거주기간_가구소득 = data_거주기간_가구소득.astype(float)
data_거주기간_맞벌이 = data_거주기간_맞벌이.astype(float)
data_거주기간_주거점유형태 = data_거주기간_주거점유형태.astype(float)

# 그래프

fig, axes = plt.subplots(8, 2, constrained_layout=True, sharey=True)
fig.subplots_adjust(top=8, wspace=1)
# fig.suptitle('성별 월평균 가구소득과 소비지출액', fontsize=16, fontweight='bold')

# 거주의사 그래프
읍면동_거주의사_graph = data_거주의사_읍면동.plot.bar(ax=axes[0][0], fontsize=15, stacked=True, rot=0,
                                        color=['crimson', 'coral', 'lemonchiffon', 'chartreuse', 'deepskyblue',
                                               'midnightblue', 'darkviolet', 'hotpink'])
읍면동_거주의사_graph.set_xticklabels(['조치원읍', '면지역', '동지역'])
읍면동_거주의사_graph.set_title('읍면동별 거주의사', fontsize=20)
읍면동_거주의사_graph.legend(loc='center left', bbox_to_anchor=(1, 0.5))
for p in 읍면동_거주의사_graph.patches:
    x, y, width, height = p.get_bbox().bounds
    if height == 0.0:
        continue
    읍면동_거주의사_graph.text(x + width, y + height / 2, "%.1f %%" % (height), va='center', fontsize=12)

# 거주기간 그래프
읍면동_거주기간_graph = data_거주기간_읍면동.plot.bar(ax=axes[0][1], fontsize=15, stacked=True, rot=0,
                                        color=['lightpink', 'crimson', 'coral', 'lemonchiffon', 'chartreuse',
                                               'deepskyblue', 'midnightblue', 'darkviolet'])
읍면동_거주기간_graph.set_xticklabels(['조치원읍', '면지역', '동지역'])
읍면동_거주기간_graph.set_title('읍면동별 거주기간', fontsize=20)
읍면동_거주기간_graph.legend(loc='center left', bbox_to_anchor=(1, 0.5))
for p in 읍면동_거주기간_graph.patches:
    x, y, width, height = p.get_bbox().bounds
    if height == 0.0:
        continue
    읍면동_거주기간_graph.text(x + width, y + height / 2, "%.1f %%" % (height), va='center', fontsize=10)

# 거주의사 그래프
성별_거주의사_graph = data_거주의사_성별.plot.bar(ax=axes[1][0], stacked=True, rot=0, fontsize=15,
                                      color=['crimson', 'coral', 'lemonchiffon', 'chartreuse', 'deepskyblue',
                                             'midnightblue', 'darkviolet', 'hotpink'])
# 성별_소득_graph = 성별_graph.add_subplot(2, 2, 1)
성별_거주의사_graph.set_xticklabels(['남성', '여성'])
성별_거주의사_graph.set_title('성별 거주의사', fontsize=20)
성별_거주의사_graph.legend(loc='center left', bbox_to_anchor=(1, 0.5))
for p in 성별_거주의사_graph.patches:
    x, y, width, height = p.get_bbox().bounds
    if height == 0.0:
        continue
    성별_거주의사_graph.text(x + width, y + height / 2, "%.1f %%" % (height), va='center', ha='center', fontsize=12)

# 거주기간 그래프
성별_거주기간_graph = data_거주기간_성별.plot.bar(ax=axes[1][1], stacked=True, rot=0, fontsize=15,
                                      color=['lightpink', 'crimson', 'coral', 'lemonchiffon', 'chartreuse',
                                             'deepskyblue', 'midnightblue', 'darkviolet'])
성별_거주기간_graph.set_xticklabels(['남성', '여성'])
성별_거주기간_graph.set_title('성별 거주기간', fontsize=20)
성별_거주기간_graph.legend(loc='center left', bbox_to_anchor=(1, 0.5))
for p in 성별_거주기간_graph.patches:
    x, y, width, height = p.get_bbox().bounds
    if height == 0.0:
        continue
    성별_거주기간_graph.text(x + width, y + height / 2, "%.1f %%" % (height), va='center', fontsize=12)

# 거주의사 그래프
연령_거주의사_graph = data_거주의사_연령.plot.bar(ax=axes[2][0], fontsize=15, stacked=True, rot=0,
                                      color=['crimson', 'coral', 'lemonchiffon', 'chartreuse', 'deepskyblue',
                                             'midnightblue', 'darkviolet', 'hotpink'])
연령_거주의사_graph.set_xticklabels(['13-19세', '20-29세', '30-39세', '40-49세', '50-59세', '60세이상', '65세이상'], rotation=45)
연령_거주의사_graph.set_title('연령별 거주의사', fontsize=20)
연령_거주의사_graph.legend(loc='center left', bbox_to_anchor=(1, 0.5))
for p in 연령_거주의사_graph.patches:
    x, y, width, height = p.get_bbox().bounds
    if height == 0.0:
        continue
    연령_거주의사_graph.text(x + width, y + height / 2, "%.1f %%" % (height), va='center', fontsize=8)

# 거주기간 그래프
연령_거주기간_graph = data_거주기간_연령.plot.bar(ax=axes[2][1], fontsize=15, stacked=True, rot=0,
                                      color=['lightpink', 'crimson', 'coral', 'lemonchiffon', 'chartreuse',
                                             'deepskyblue', 'midnightblue', 'darkviolet'])
연령_거주기간_graph.set_xticklabels(['13-19세', '20-29세', '30-39세', '40-49세', '50-59세', '60세이상', '65세이상'], rotation=45)
연령_거주기간_graph.set_title('연령별 거주기간', fontsize=20)
연령_거주기간_graph.legend(loc='center left', bbox_to_anchor=(1, 0.5))
for p in 연령_거주기간_graph.patches:
    x, y, width, height = p.get_bbox().bounds
    if height == 0.0:
        continue
    연령_거주기간_graph.text(x + width, y + height / 2, "%.1f %%" % (height), va='center', fontsize=8)

# 거주의사 그래프
교육정도_거주의사_graph = data_거주의사_교육정도.plot.bar(ax=axes[3][0], fontsize=15, stacked=True, rot=0,
                                          color=['crimson', 'coral', 'lemonchiffon', 'chartreuse', 'deepskyblue',
                                                 'midnightblue', 'darkviolet', 'hotpink'])
교육정도_거주의사_graph.set_xticklabels(['초졸이하', '중졸', '고졸', '대학이상'])
교육정도_거주의사_graph.set_title('교육정도별 거주의사', fontsize=20)
교육정도_거주의사_graph.legend(loc='center left', bbox_to_anchor=(1, 0.5))
for p in 교육정도_거주의사_graph.patches:
    x, y, width, height = p.get_bbox().bounds
    if height == 0.0:
        continue
    교육정도_거주의사_graph.text(x + width, y + height / 2, "%.1f %%" % (height), va='center', fontsize=12)

# 거주기간 그래프
교육정도_거주기간_graph = data_거주기간_교육정도.plot.bar(ax=axes[3][1], fontsize=15, stacked=True, rot=0,
                                          color=['lightpink', 'crimson', 'coral', 'lemonchiffon', 'chartreuse',
                                                 'deepskyblue', 'midnightblue', 'darkviolet'])
교육정도_거주기간_graph.set_xticklabels(['초졸이하', '중졸', '고졸', '대학이상'])
교육정도_거주기간_graph.set_title('교육정도별 거주기간', fontsize=20)
교육정도_거주기간_graph.legend(loc='center left', bbox_to_anchor=(1, 0.5))
for p in 교육정도_거주기간_graph.patches:
    x, y, width, height = p.get_bbox().bounds
    if height == 0.0:
        continue
    교육정도_거주기간_graph.text(x + width, y + height / 2, "%.1f %%" % (height), va='center', fontsize=12)

# 거주의사 그래프
직업_거주의사_graph = data_거주의사_직업.plot.bar(ax=axes[4][0], fontsize=15, stacked=True, rot=0,
                                      color=['crimson', 'coral', 'lemonchiffon', 'chartreuse', 'deepskyblue',
                                             'midnightblue', 'darkviolet', 'hotpink'])
직업_거주의사_graph.set_xticklabels(['전문관리', '사무', '서비스판매', '농어업', '기능노무', '군인/주부/학생/무직'], rotation=20)
직업_거주의사_graph.set_title('직업별 거주의사', fontsize=20)
직업_거주의사_graph.legend(loc='center left', bbox_to_anchor=(1, 0.5))
for p in 직업_소득_graph.patches:
    x, y, width, height = p.get_bbox().bounds
    if height == 0.0:
        continue
    직업_거주의사_graph.text(x + width, y + height / 2, "%.1f %%" % (height), va='center', fontsize=10)

# 거주기간 그래프
직업_거주기간_graph = data_거주기간_직업.plot.bar(ax=axes[4][1], fontsize=15, stacked=True, rot=0,
                                      color=['lightpink', 'crimson', 'coral', 'lemonchiffon', 'chartreuse',
                                             'deepskyblue', 'midnightblue', 'darkviolet'])
직업_거주기간_graph.set_xticklabels(['전문관리', '사무', '서비스판매', '농어업', '기능노무', '군인/주부/학생/무직'], rotation=20)
직업_거주기간_graph.set_title('직업별 거주기간', fontsize=20)
직업_거주기간_graph.legend(loc='center left', bbox_to_anchor=(1, 0.5))
for p in 직업_거주기간_graph.patches:
    x, y, width, height = p.get_bbox().bounds
    if height == 0.0:
        continue
    직업_거주기간_graph.text(x + width, y + height / 2, "%.1f %%" % (height), va='center', fontsize=10)

# 거주의사 그래프
혼인상태_거주의사_graph = data_거주의사_혼인상태.plot.bar(ax=axes[5][0], fontsize=15, stacked=True, rot=0,
                                          color=['crimson', 'coral', 'lemonchiffon', 'chartreuse', 'deepskyblue',
                                                 'midnightblue', 'darkviolet', 'hotpink'])
혼인상태_거주의사_graph.set_xticklabels(['미혼', '유배우', '사별/이혼'])
혼인상태_거주의사_graph.set_title('혼인상태별 거주의사', fontsize=20)
혼인상태_거주의사_graph.legend(loc='center left', bbox_to_anchor=(1, 0.5))
for p in 혼인상태_거주의사_graph.patches:
    x, y, width, height = p.get_bbox().bounds
    if height == 0.0:
        continue
    혼인상태_거주의사_graph.text(x + width, y + height / 2, "%.1f %%" % (height), va='center', fontsize=10)

# 거주기간 그래프
혼인상태_거주기간_graph = data_거주기간_혼인상태.plot.bar(ax=axes[5][1], fontsize=15, stacked=True, rot=0,
                                          color=['lightpink', 'crimson', 'coral', 'lemonchiffon', 'chartreuse',
                                                 'deepskyblue', 'midnightblue', 'darkviolet'])
혼인상태_거주기간_graph.set_xticklabels(['미혼', '유배우', '사별/이혼'])
혼인상태_거주기간_graph.set_title('혼인상태별 거주기간', fontsize=20)
혼인상태_거주기간_graph.legend(loc='center left', bbox_to_anchor=(1, 0.5))
for p in 혼인상태_거주기간_graph.patches:
    x, y, width, height = p.get_bbox().bounds
    if height == 0.0:
        continue
    혼인상태_거주기간_graph.text(x + width, y + height / 2, "%.1f %%" % (height), va='center', fontsize=10)

# 거주의사 그래프
맞벌이여부_거주의사_graph = data_거주의사_맞벌이.plot.bar(ax=axes[6][0], fontsize=15, stacked=True, rot=0,
                                          color=['crimson', 'coral', 'lemonchiffon', 'chartreuse', 'deepskyblue',
                                                 'midnightblue', 'darkviolet', 'hotpink'])
맞벌이여부_거주의사_graph.set_xticklabels(['맞벌이', '맞벌이안함'])
맞벌이여부_거주의사_graph.set_title('맞벌이여부별 거주의사', fontsize=20)
맞벌이여부_거주의사_graph.legend(loc='center left', bbox_to_anchor=(1, 0.5))
for p in 맞벌이여부_거주의사_graph.patches:
    x, y, width, height = p.get_bbox().bounds
    if height == 0.0:
        continue
    맞벌이여부_거주의사_graph.text(x + width, y + height / 2, "%.1f %%" % (height), va='center', fontsize=12)

# 거주기간 그래프
맞벌이여부_거주기간_graph = data_거주기간_맞벌이.plot.bar(ax=axes[6][1], fontsize=15, stacked=True, rot=0,
                                          color=['lightpink', 'crimson', 'coral', 'lemonchiffon', 'chartreuse',
                                                 'deepskyblue', 'midnightblue', 'darkviolet'])
맞벌이여부_거주기간_graph.set_xticklabels(['맞벌이', '맞벌이안함'])
맞벌이여부_거주기간_graph.set_title('맞벌이여부별 거주기간', fontsize=20)
맞벌이여부_거주기간_graph.legend(loc='center left', bbox_to_anchor=(1, 0.5))
for p in 맞벌이여부_거주기간_graph.patches:
    x, y, width, height = p.get_bbox().bounds
    if height == 0.0:
        continue
    맞벌이여부_거주기간_graph.text(x + width, y + height / 2, "%.1f %%" % (height), va='center', fontsize=12)

# 거주의사 그래프
주거점유형태_거주의사_graph = data_거주의사_주거점유형태.plot.bar(ax=axes[7][0], fontsize=15, stacked=True, rot=0,
                                              color=['crimson', 'coral', 'lemonchiffon', 'chartreuse', 'deepskyblue',
                                                     'midnightblue', 'darkviolet', 'hotpink'])
주거점유형태_거주의사_graph.set_xticklabels(['자가집', '전세', '월세/기타'])
주거점유형태_거주의사_graph.set_title('주거점유형태별 거주의사', fontsize=20)
주거점유형태_거주의사_graph.legend(loc='center left', bbox_to_anchor=(1, 0.5))
for p in 주거점유형태_거주의사_graph.patches:
    x, y, width, height = p.get_bbox().bounds
    if height == 0.0:
        continue
    주거점유형태_거주의사_graph.text(x + width, y + height / 2, "%.1f %%" % (height), va='center', fontsize=12)

# 거주기간 그래프
주거점유형태_거주기간_graph = data_거주기간_주거점유형태.plot.bar(ax=axes[7][1], fontsize=15, stacked=True, rot=0,
                                              color=['lightpink', 'crimson', 'coral', 'lemonchiffon', 'chartreuse',
                                                     'deepskyblue', 'midnightblue', 'darkviolet'])
주거점유형태_거주기간_graph.set_xticklabels(['자가집', '전세', '월세/기타'])
주거점유형태_거주기간_graph.set_title('주거점유형태별 거주기간', fontsize=20)
주거점유형태_거주기간_graph.legend(loc='center left', bbox_to_anchor=(1, 0.5))
for p in 주거점유형태_거주기간_graph.patches:
    x, y, width, height = p.get_bbox().bounds
    if height == 0.0:
        continue

    주거점유형태_거주기간_graph.text(x + width, y + height / 2, "%.1f %%" % (height), va='center', fontsize=12)

# 거주기간별 거주의사 그래프
거주의사_거주기간_graph = plt.rcParams["figure.figsize"] = (15, 10)
fig.subplots_adjust(top=1.3, wspace=0.3)
거주의사_거주기간_graph = data_거주의사_거주기간.plot.bar(stacked=True, rot=0,
                                          color=['lightpink', 'crimson', 'coral', 'lemonchiffon', 'chartreuse',
                                                 'deepskyblue', 'midnightblue', 'darkviolet'])
거주의사_거주기간_graph.set_xticklabels(['출범이전', '출범이후'])
거주의사_거주기간_graph.set_title('거주기간별 거주의사')
거주의사_거주기간_graph.legend(loc='center left', bbox_to_anchor=(1, 0.5))
for p in 거주의사_거주기간_graph.patches:
    x, y, width, height = p.get_bbox().bounds
    if height == 0.0:
        continue
    거주의사_거주기간_graph.text(x + width, y + height / 2, "%.1f %%" % (height), va='center')

## 표제부

# 자료 불러오기
표제부 = pd.read_csv(input_path.joinpath('2.세종시_표제부.csv'))

# 세종 특별자치시 없애기
for i in range(len(표제부['대지위치'])):
    표제부['대지위치'][i] = 표제부['대지위치'][i][9:]
표제부

표제부['주소'] = 표제부['대지위치']

# 동만 남기기
for i in range(len(표제부['대지위치'])):
    표제부['주소'][i] = 표제부['주소'][i][:3]
    표제부['대지위치'][i] = 표제부['대지위치'][i][3:]
표제부

pd.set_option('display.max_rows', 6010)
data_표제부 = 표제부.groupby(['주소', '대지구분코드', '주용도코드명', '건물명', '구조코드명', '동명칭'])[['세대수(세대)', '연면적(㎡)']].sum()
data_표제부

## 전유부

# 자료 불러오기
전유부 = pd.read_csv(input_path.joinpath('1.세종시_전유부.csv'))

# 세종 특별자치시 없애기
for i in range(len(전유부['대지위치'])):
    전유부['대지위치'][i] = 전유부['대지위치'][i][9:]
전유부

전유부['주소'] = 전유부['대지위치']

# 동만 남기기
for i in range(len(전유부['대지위치'])):
    전유부['주소'][i] = 전유부['주소'][i][:3]
    전유부['대지위치'][i] = 전유부['대지위치'][i][3:]
전유부

pd.set_option('display.max_rows', 3700)
data_전유부 = 전유부.groupby(['주소', '대지위치', '대지구분코드', '건물명', '동명칭', '호명칭', '층구분코드명'])[['층번호']].max()
data_전유부

## 개별공시지가 그래프

# 자료 불러오기
공시지가 = pd.read_csv(input_path.joinpath('18.세종시_개별공시지가(2017~2020).csv'))
공시지가

# 법정동명 - 기준년도 별 공시지가 표
data_공시지가 = 공시지가.groupby(['법정동명', '기준년도'])[['공시지가']].mean()
data_공시지가

data_공시지가 = data_공시지가.reset_index()
data_공시지가

# 세종특별자치시 제거
pd.set_option('display.max_rows', 6010)
for i in range(len(data_공시지가['법정동명'])):
    data_공시지가['법정동명'][i] = data_공시지가['법정동명'][i][8:]
data_공시지가

# 법정동면을 법정경계이름으로 편집

data_공시지가['num'] = 0
for i in range(len(data_공시지가['기준년도'])):
    data_공시지가['num'][i] = len(data_공시지가['법정동명'][i])
data_공시지가

for i in range(len(data_공시지가['법정동명'])):
    if (len(data_공시지가['법정동명'][i]) == 4):
        data_공시지가['법정동명'][i] = data_공시지가['법정동명'][i][1:]
    elif (len(data_공시지가['법정동명'][i]) == 8):
        if (data_공시지가['법정동명'][i][1:5] == '조치원읍'):
            data_공시지가['법정동명'][i] = data_공시지가['법정동명'][i][1:5]
        elif (data_공시지가['법정동명'][i][:4] == '조치원읍'):
            data_공시지가['법정동명'][i] = data_공시지가['법정동명'][i][:4]
        else:
            data_공시지가['법정동명'][i] = data_공시지가['법정동명'][i][1:4]
    elif (len(data_공시지가['법정동명'][i]) == 9):
        data_공시지가['법정동명'][i] = data_공시지가['법정동명'][i][1:5]
    elif (len(data_공시지가['법정동명'][i]) == 7):
        if (data_공시지가['법정동명'][i][:4] == '조치원읍'):
            data_공시지가['법정동명'][i] = data_공시지가['법정동명'][i][:4]
        else:
            data_공시지가['법정동명'][i] = data_공시지가['법정동명'][i][:3]

for i in range(len(data_공시지가['기준년도'])):
    data_공시지가['num'][i] = len(data_공시지가['법정동명'][i])
data_공시지가

data_공시지가 = data_공시지가[['법정동명', '기준년도', '공시지가']]
data_공시지가

data_공시지가['공시지가'] = round(data_공시지가['공시지가'], 3)
data_공시지가

data_공시지가 = round(pd.crosstab(index=[data_공시지가.법정동명], columns=data_공시지가.기준년도, values=data_공시지가.공시지가, aggfunc=np.mean,
                              margins=True).fillna(0), 3)
data_공시지가 = data_공시지가.drop(['All'])
del (data_공시지가['All'])
data_공시지가

data_공시지가 = data_공시지가.reset_index()
data_공시지가

data_공시지가_지역 = np.transpose(data_공시지가)
data_공시지가_지역 = data_공시지가_지역.drop(['법정동명'])
data_공시지가_지역

data_공시지가_지역 = data_공시지가_지역.reset_index()
data_공시지가_지역 = data_공시지가_지역[[0, 1, 2, 3, 4, 5, 6, 7,
                             8, 9, 10, 11, 12, 13, 14, 15, 16,
                             17, 18, 19, 20, 21, 22, 23, 24, 25,
                             26, 27]]
data_공시지가_지역 = data_공시지가_지역.rename(columns={0: '가람동', 1: '고운동', 2: '금남면', 3: '나성동', 4: '다정동', 5: '대평동', 6: '도담동',
                                            7: '반곡동', 8: '보람동', 9: '부강면', 10: '산울동', 11: '새롬동', 12: '소담동', 13: '소정면',
                                            14: '아름동', 15: '어진동', 16: '연기면', 17: '연동면', 18: '연서면', 29: '장군면', 20: '전동면',
                                            21: '전의면', 22: '조치원읍', 23: '종촌동', 24: '집현동', 25: '한솔동', 26: '합강동',
                                            27: '해밀동'})
data_공시지가_지역

# 지역별 연도별 공시지가 그래프
style.use('seaborn-talk')
fig = plt.figure(figsize=(70, 23))
ax = fig.add_subplot(111, projection='3d')

# x : 지역 / y : 연도 / z : 공시지가
k = 0
colors = ['lightcoral', 'burlywood', 'yellowgreen', 'royalblue']
address = ['가람동', '고운동', '금남면', '나성동', '다정동', '대평동', '도담동',
           '반곡동', '보람동', '부강면', '산울동', '새롬동', '소담동', '소정면',
           '아름동', '어진동', '연기면', '연동면', '연서면', '장군면', '전동면',
           '전의면', '조치원읍', '종촌동', '집현동', '한솔동', '합강동', '해밀동']
years = ['2017', '2018', '2019', '2020']
year = [1, 2, 3, 4]

for c, r in zip(colors, [0, 1, 2, 3]):
    indexs = address
    tmp = data_공시지가_지역.iloc[k]
    tmp = tmp.reset_index()
    # print(tmp)
    tmp = np.array(tmp[k].tolist())
    heights = tmp
    ax.bar(indexs, heights, zs=r, zdir='y', color=c, alpha=0.8)
    k = k + 1

ax.set_yticks(np.arange(0, 4, 1))
ax.set_yticklabels(years, fontsize=20, rotation=-20)
ax.set_xticks(np.arange(0, 28, 1))
ax.set_xticklabels(address, rotation=45, fontsize=15)
ax.set_zticklabels(['0', '50만', '100만', '150만', '200만', '250만', '300만'], fontsize=20)
ax.set_ylabel('연도', fontsize=30)
ax.set_xlabel('지역', fontsize=30)
ax.set_zlabel('공시지가', fontsize=30)

## 상업업무용 실거래가 지도

# 자료 불러오기
상업실거래가 = pd.read_csv(input_path.joinpath('11.세종시_상업업무용(매매)_실거래가.csv'))
상업실거래가

# 시군구 - 용도지역 - 거래금액 표 만들기

상업실거래가['거래금액(만원)'] = 상업실거래가['거래금액(만원)'].apply(lambda x: float(x.split()[0].replace(',', '')))
data_상업실거래가 = 상업실거래가.groupby(['시군구', '유형', '도로명', '용도지역', '건축물주용도'])[['거래금액(만원)']].mean()
data_상업실거래가

data_상업실거래가 = data_상업실거래가.reset_index()
data_상업실거래가 = data_상업실거래가[['시군구', '용도지역', '거래금액(만원)']]
data_상업실거래가

data_상업실거래가 = 상업실거래가.groupby(['시군구', '용도지역'])[['거래금액(만원)']].mean().reset_index()

# 세종특별자치시 제거
pd.set_option('display.max_rows', 6010)
for i in range(len(data_상업실거래가['시군구'])):
    if data_상업실거래가['시군구'][i][-1] == '리':
        data_상업실거래가['시군구'][i] = data_상업실거래가['시군구'][i][8:12]
    else:
        data_상업실거래가['시군구'][i] = data_상업실거래가['시군구'][i][8:]
data_상업실거래가 = round(data_상업실거래가.groupby(['시군구', '용도지역'])[['거래금액(만원)']].mean(), 3)
data_상업실거래가

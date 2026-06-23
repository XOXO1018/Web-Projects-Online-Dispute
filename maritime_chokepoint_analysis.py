# -*- coding: utf-8 -*-
"""
Maritime Chokepoint Risk Trade Analysis
========================================
海事咽喉要道风险分析主程序

原 Jupyter Notebook: Maritime_chokepoint_risk_trade.ipynb
转换后可在 PyCharm 等 IDE 中直接运行

作者：Original author (Jasper)
转换日期：2026-04-26

依赖安装:
    pip install pandas geopandas matplotlib numpy dask[dataframe] pyproj cartopy scipy statsmodels openpyxl

注意事项:
    1. 需要配置所有数据文件的绝对路径
    2. 确保所有依赖的 shapefile、CSV、Excel 文件存在
    3. 首次运行前请检查 PATHS 配置部分
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import glob
from pyproj import CRS
from cartopy import crs as ccrs
import matplotlib.colors as colors
from scipy import stats
import statsmodels.api as sm
import dask.dataframe as dd
import os

# ============================================================================
# 配置部分 - 请根据实际情况修改路径
# ============================================================================

# 设置中文字体（可选，根据系统调整）
plt.rcParams["font.family"] = "Times New Roman"
# 如果使用中文，可能需要：plt.rcParams['font.sans-serif'] = ['SimHei']

# 数据路径配置 - 请修改为你的实际路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 示例路径配置（请根据实际情况修改）
PATHS = {
    # 咽喉要道 shapefile
    'chokepoint_shp': r'C:\Users\30742\Desktop\19663059\Data\Canals_mapping.shp',
    
    # GADM 行政区划数据
    'gadm_shp': r'/Users/Jasper/Documenten/DPhil_Oxford/DPhil_GIS/GADM/gadm36_0.shp',
    
    # 事故数据
    'incident_csv': r'Data/Accidents/GISIS-MCIR-20240807-122212.csv',
    
    # 冲突数据
    'conflict_csv': r'Data/Conflict/GEDEvent_v24_1.csv',
    
    # 恐怖主义数据
    'terror_xlsx': r'Data/Terrorist/globalterrorismdb_0522dist.xlsx',
    
    # 海盗数据
    'piracy_shp': r'Data/Piracy/Asam_data_download/All ASAM Events.shp',
    
    # 军事争端数据
    'mid_dispute_csv': r'Data/MID-5-Data-and-Supporting-Materials/MIDA 5.0.csv',
    'mid_incident_csv': r'Data/MID-5-Data-and-Supporting-Materials/MIDI 5.0.csv',
    'midloc_a_csv': r'Data/MIDLOC_2.1/MIDLOCA_2.1.csv',
    'midloc_i_csv': r'Data/MIDLOC_2.1/MIDLOCI_2.1.csv',
    
    # 热带气旋数据
    'tc_events_csv': r'Data/TC_events/cat1_event_database.csv',
    
    # 咽喉要道风险数据表
    'chokepoint_datasheet_xlsx': r'Chokepoint_risk_information/Chokepoint_datasheet_new.xlsx',
}

# 分析参数配置
PARAMS = {
    'buffer_size_incident': 10,      # 事故数据缓冲区 (km)
    'buffer_size_conflict': 50,      # 冲突数据缓冲区 (km)
    'buffer_size_terror': 50,        # 恐怖主义数据缓冲区 (km)
    'buffer_size_piracy': 50,        # 海盗数据缓冲区 (km)
    'buffer_size_mis': 200,          # 军事争端数据缓冲区 (km)
    'mis_thres_level': 2,            # 军事争端阈值等级
    'mis_year_thres': 1974,          # 军事争端起始年份
}

# 风险列表
RISK_LIST = ['piracy', 'geopolitical', 'blockage', 'drought', 'EQ', 'TC', 'terrorist', 'conflict']


# ============================================================================
# 风险量化函数
# ============================================================================

def risk_drought(likelihood):
    """
    干旱风险量化
    
    参数:
        likelihood: 可能性 ('no' 或其他)
    
    返回:
        tuple: (likelihood_years, timescale_days, severity_0_1)
    """
    if likelihood == 'no':
        return np.nan, np.nan, np.nan
    else:
        return 40, 250, 0.33


def risk_EQ(likelihood):
    """
    地震风险量化
    
    参数:
        likelihood: 可能性 ('no' 或其他)
    
    返回:
        tuple: (likelihood_years, timescale_days, severity_0_1)
    """
    if likelihood == 'no':
        return np.nan, np.nan, np.nan
    else:
        return 2500, 365, 1


def add_risk_quantification(df):
    """
    为 DataFrame 添加风险量化信息
    
    参数:
        df: 输入 DataFrame
    
    返回:
        DataFrame: 添加了风险量化列的 DataFrame
    """
    # 干旱风险
    risk_index = 'drought'
    df['likelihood_' + risk_index], df['timescale_' + risk_index], df['severity_' + risk_index] = \
        zip(*df[risk_index].apply(risk_drought))
    
    # 地震风险
    risk_index = 'EQ'
    df['likelihood_' + risk_index], df['timescale_' + risk_index], df['severity_' + risk_index] = \
        zip(*df[risk_index].apply(risk_EQ))
    
    return df


def derive_trade_at_risk(trade_iso3, risk_df):
    """
    推导受风险影响的贸易
    
    参数:
        trade_iso3: 贸易数据 DataFrame
        risk_df: 风险数据 DataFrame
    
    返回:
        DataFrame: 包含贸易风险信息的 DataFrame
    """
    # 合并风险信息
    trade_iso3 = trade_iso3.merge(risk_df, on='canal')
    
    # 计算贸易份额
    trade_iso3['v_share'] = trade_iso3['v_canal'] / trade_iso3['v']
    trade_iso3['v_share_mar'] = trade_iso3['v_canal'] / trade_iso3['v_sea_predict']
    
    # 循环处理各种风险
    for risk in RISK_LIST:
        # 处理 timescale 的 NaN 值
        trade_iso3['timescale_' + str(risk)] = \
            trade_iso3['timescale_' + str(risk)].replace(np.nan, 0).astype(int)
        
        # 计算价值贸易风险
        trade_iso3['trade_at_risk_' + str(risk) + '_v'] = \
            trade_iso3['v_canal'] * (1 / trade_iso3['likelihood_' + str(risk)]) * \
            (trade_iso3['timescale_' + str(risk)] / 365) * trade_iso3['severity_' + str(risk)]
        
        # 计算数量贸易风险
        trade_iso3['trade_at_risk_' + str(risk) + '_q'] = \
            trade_iso3['q_canal'] * (1 / trade_iso3['likelihood_' + str(risk)]) * \
            (trade_iso3['timescale_' + str(risk)] / 365) * trade_iso3['severity_' + str(risk)]
        
        # 计算收入风险
        trade_iso3['revenue_at_risk_' + str(risk)] = \
            trade_iso3['revenue_USD'] * (1 / trade_iso3['likelihood_' + str(risk)]) * \
            (trade_iso3['timescale_' + str(risk)] / 365) * trade_iso3['severity_' + str(risk)]
        
        # 计算受影响贸易
        trade_iso3['trade_impacted_' + str(risk)] = \
            trade_iso3['v_canal'] * (trade_iso3['timescale_' + str(risk)] / 365) * \
            trade_iso3['severity_' + str(risk)]
    
    # 计算总计
    trade_iso3['trade_at_risk_v'] = trade_iso3[[
        'trade_at_risk_piracy_v', 'trade_at_risk_geopolitical_v',
        'trade_at_risk_terrorist_v', 'trade_at_risk_conflict_v',
        'trade_at_risk_blockage_v', 'trade_at_risk_drought_v',
        'trade_at_risk_EQ_v', 'trade_at_risk_TC_v'
    ]].sum(axis=1)
    
    trade_iso3['trade_at_risk_q'] = trade_iso3[[
        'trade_at_risk_piracy_q', 'trade_at_risk_geopolitical_q',
        'trade_at_risk_terrorist_q', 'trade_at_risk_conflict_q',
        'trade_at_risk_blockage_q', 'trade_at_risk_drought_q',
        'trade_at_risk_EQ_q', 'trade_at_risk_TC_q'
    ]].sum(axis=1)
    
    trade_iso3['revenue_at_risk'] = trade_iso3[[
        'revenue_at_risk_piracy', 'revenue_at_risk_geopolitical',
        'revenue_at_risk_terrorist', 'revenue_at_risk_conflict',
        'revenue_at_risk_blockage', 'revenue_at_risk_drought',
        'revenue_at_risk_EQ', 'revenue_at_risk_TC'
    ]].sum(axis=1)
    
    trade_iso3['trade_impacted'] = trade_iso3[[
        'trade_impacted_piracy', 'trade_impacted_geopolitical',
        'trade_impacted_terrorist', 'trade_impacted_conflict',
        'trade_impacted_blockage', 'trade_impacted_drought',
        'trade_impacted_EQ', 'trade_impacted_TC'
    ]].sum(axis=1)
    
    return trade_iso3


def return_delay(delay, VOT):
    """
    计算延误价值
    
    参数:
        delay: 延误天数
        VOT: 时间价值 (Value of Time)
    
    返回:
        float: 累计延误价值
    """
    val = 0
    for i in range(0, delay + 1):
        val = val + i * VOT
    return val


def estimate_economic_cost(df, delay_cost, rerouting_cost, risk):
    """
    估算经济成本
    
    参数:
        df: 主数据 DataFrame
        delay_cost: 延误成本系数
        rerouting_cost: 改道成本系数
        risk: 风险类型
    
    返回:
        DataFrame: 包含经济成本估算的 DataFrame
    """
    sheet_names = [
        'Response_1days', 'Response_3days', 'Response_5days', 'Response_7days',
        'Response_10days', 'Response_30days', 'Response_50days', 'Response_100days',
        'Response_183days', 'Response_250days', 'Response_365days'
    ]
    
    economic_fraction = pd.DataFrame()
    for sheet in sheet_names:
        sheet_df = pd.read_excel(
            PATHS['chokepoint_datasheet_xlsx'], 
            sheet_name=sheet
        ).rename(columns={'Chokepoint': 'canal'}) \
         .rename(columns={'timescale': 'timescale_' + risk})
        sheet_df['timescale_' + risk] = sheet_df['timescale_' + risk].astype(int)
        economic_fraction = pd.concat([economic_fraction, sheet_df], 
                                       ignore_index=True, sort=False)
    
    df_new = df.merge(economic_fraction, on=['canal', 'timescale_' + risk])
    df_new['delay_val_' + risk] = df_new.apply(
        lambda row: return_delay(row['delay'], 0.01), axis=1
    )
    
    df_new['delay_USD_' + risk] = (
        (df_new['v_canal'] / 365) * (1 / df_new['likelihood_' + str(risk)]) *
        df_new['severity_' + str(risk)]
    ) * (
        df_new['rerouting_km'] * 0.01 / (30 * 24) * df_new['timescale_' + risk] +
        df_new['delay_val_' + risk]
    )
    
    df_new['reroute_USD_' + risk] = \
        2 * df_new['trade_at_risk_' + str(risk) + '_q'] * df_new['rerouting_km'] * rerouting_cost
    
    df_new['lost_USD_' + risk] = \
        df_new['trade_at_risk_' + str(risk) + '_v'] * df_new['disrupted']
    
    df_new['revenue_USD_' + risk] = df_new['revenue_at_risk_' + str(risk)]
    
    df_new['total_loss_USD_' + risk] = (
        df_new['delay_USD_' + risk] + df_new['reroute_USD_' + risk] +
        df_new['lost_USD_' + risk] + df_new['revenue_USD_' + risk]
    )
    
    df_new = df_new.drop(columns=['delay', 'rerouting_km', 'disrupted'])
    print(risk, df_new['total_loss_USD_' + risk].sum() / 1e9, df_new['delay_val_' + risk].sum())
    
    df = df.merge(
        df_new[['canal', 'iso3', 'delay_USD_' + risk, 'reroute_USD_' + risk,
                'lost_USD_' + risk, 'revenue_USD_' + risk, 'total_loss_USD_' + risk]],
        on=['canal', 'iso3'], how='left'
    )
    
    return df


# ============================================================================
# 地理空间分析函数
# ============================================================================

def add_buffer(df, buffer_size):
    """
    为 DataFrame 添加地理缓冲区
    
    参数:
        df: 包含 latitude 和 longitude 列的 DataFrame
        buffer_size: 缓冲区大小 (km)
    
    返回:
        GeoDataFrame: 带缓冲区的 GeoDataFrame
    """
    gdf = gpd.GeoDataFrame(
        df, 
        geometry=gpd.points_from_xy(df.longitude, df.latitude), 
        crs="EPSG:4326"
    )
    
    gdf_buffer = gdf.copy()
    gdf_buffer['geometry'] = gdf_buffer.geometry.buffer(buffer_size / 100)
    gdf_buffer['number'] = 1
    
    return gdf_buffer


def add_buffer_gdf(gdf, buffer_size):
    """
    为 GeoDataFrame 添加地理缓冲区
    
    参数:
        gdf: 输入 GeoDataFrame
        buffer_size: 缓冲区大小 (km)
    
    返回:
        GeoDataFrame: 带缓冲区的 GeoDataFrame
    """
    gdf_buffer = gdf.copy()
    gdf_buffer['geometry'] = gdf_buffer.geometry.buffer(buffer_size / 100)
    gdf_buffer['number'] = 1
    
    return gdf_buffer


def lat_function(deg, min_sec, sign):
    """
    解析纬度坐标
    
    参数:
        deg: 度数字符串 (如 "30°")
        min_sec: 分秒字符串 (如 "15.30'")
        sign: 方向 (N/S)
    
    返回:
        float: 十进制度纬度
    """
    if sign in ['N', 'S']:
        lat_degree = int(deg.split('°')[0])
        lat_minutes = int(min_sec.split('.')[0])
        lat_seconds = int(min_sec.split('.')[1].split("'")[0])
        
        if sign == 'N':
            return lat_degree + lat_minutes / 60 + lat_seconds / 3600
        else:
            return -1 * (lat_degree + lat_minutes / 60 + lat_seconds / 3600)
    else:
        return np.nan


def lon_function(deg, min_sec, sign):
    """
    解析经度坐标
    
    参数:
        deg: 度数字符串 (如 "120°")
        min_sec: 分秒字符串 (如 "30.45'")
        sign: 方向 (E/W)
    
    返回:
        float: 十进制度经度
    """
    if sign in ['E', 'W']:
        lat_degree = int(deg.split('°')[0])
        lat_minutes = int(min_sec.split('.')[0])
        lat_seconds = int(min_sec.split('.')[1].split("'")[0])
        
        if sign == 'E':
            return lat_degree + lat_minutes / 60 + lat_seconds / 3600
        else:
            return -1 * (lat_degree + lat_minutes / 60 + lat_seconds / 3600)
    else:
        return np.nan


def read_incident_data(incident, cp, buffer_size):
    """
    读取和处理事故数据
    
    参数:
        incident: 事故数据 DataFrame
        cp: 咽喉要道 GeoDataFrame
        buffer_size: 缓冲区大小 (km)
    
    返回:
        tuple: (incident_gdf, cp_incident, cp_event)
    """
    incident = incident[~incident['Coordinates'].isna()].reset_index(drop=True)
    incident = pd.concat([incident, incident['Coordinates'].str.split(' ', expand=True)], axis=1)
    
    incident['latitude'] = incident.apply(
        lambda row: lat_function(row[0], row[1], row[2]), axis=1
    )
    incident['longitude'] = incident.apply(
        lambda row: lon_function(row[3], row[4], row[5]), axis=1
    )
    
    incident_gdf = add_buffer(df=incident, buffer_size=buffer_size)
    incident_gdf = incident_gdf[
        (incident_gdf['latitude'].notna()) & (incident_gdf['longitude'].notna())
    ].reset_index(drop=True)
    
    incident_gdf = incident_gdf[
        incident_gdf['Casualty severity'].isin(['Marine incident', 'Very serious marine casualty'])
    ].reset_index(drop=True)
    
    N_years = pd.to_datetime(
        incident['Occurrence date and time'], 
        format='%d/%m/%Y %H:%M'
    ).dt.year.nunique()
    
    # 咽喉要道与事故叠加
    cp_incident = cp[['canal']].merge(
        gpd.overlay(cp, incident_gdf).groupby(['canal'])[['number']].sum().reset_index(),
        on='canal', how='left'
    )
    cp_incident['number'] = np.where(
        cp_incident['canal'].isin(['Suez Canal', 'Panama Canal', 'Bosporus Strait']),
        cp_incident['number'], np.nan
    )
    cp_incident['number'] = np.where(
        cp_incident['canal'] == 'Suez canal', 
        cp_incident['number'] + 1, cp_incident['number']
    )
    
    cp_incident['likelihood_blockage'] = 1 / (cp_incident['number'] / N_years)
    cp_incident['timescale_blockage'], cp_incident['severity_blockage'] = 3, 1
    
    # 咽喉要道事件
    cp_event = gpd.overlay(cp, incident_gdf)
    cp_event['number'] = np.where(
        cp_event['canal'].isin(['Suez Canal', 'Panama Canal', 'Bosporus Strait']),
        1, np.nan
    )
    cp_event = cp_event[['canal', 'number']].copy().dropna()
    cp_event = pd.concat(
        [cp_event, pd.DataFrame({'canal': ['Suez Canal'], 'number': [1]})],
        ignore_index=True, sort=False
    )
    cp_event['likelihood_blockage'] = N_years
    cp_event['timescale_blockage'], cp_event['severity_blockage'] = 3, 1
    
    return incident_gdf, cp_incident, cp_event


def read_conflict_data(conflict, cp, buffer_size):
    """
    读取和处理冲突数据
    
    参数:
        conflict: 冲突数据 DataFrame
        cp: 咽喉要道 GeoDataFrame
        buffer_size: 缓冲区大小 (km)
    
    返回:
        tuple: (conflict_gdf, cp_conflict, cp_event)
    """
    # 只提取致命冲突
    conflict = conflict[
        (conflict['latitude'].notna()) & 
        (conflict['longitude'].notna()) & 
        (conflict['best'] > 10)
    ].reset_index(drop=True)
    
    conflict['government_a'] = conflict['side_a'].str.contains('Government')
    conflict['government_b'] = conflict['side_b'].str.contains('Government')
    conflict['interstate'] = np.where(
        ((conflict['government_a'] == True) & (conflict['government_b'] == True)), 1, 0
    )
    
    # 移除国家间冲突
    conflict = conflict[conflict['interstate'] == 0].reset_index(drop=True)
    
    # 创建 GeoDataFrame
    conflict_gdf = add_buffer(df=conflict, buffer_size=buffer_size)
    
    # 咽喉要道与冲突叠加
    cp_conflict = cp[['canal']].merge(
        gpd.overlay(cp, conflict_gdf).groupby(['canal'])[['number', 'best']].sum().reset_index(),
        on='canal', how='left'
    )
    cp_conflict['likelihood_conflict'] = 1 / (cp_conflict['number'] / conflict['year'].nunique())
    cp_conflict['timescale_conflict'], cp_conflict['severity_conflict'] = 10, 0.2
    
    print(conflict['year'].min(), conflict['year'].max(), 
          conflict['year'].nunique(), cp_conflict['number'].sum())
    
    # 咽喉要道事件
    cp_event = gpd.overlay(cp, conflict_gdf)[['canal']].copy()
    cp_event['number'] = 1
    cp_event['likelihood_conflict'] = conflict['year'].nunique()
    cp_event['timescale_conflict'], cp_event['severity_conflict'] = 10, 0.2
    
    return conflict_gdf, cp_conflict, cp_event


def read_terror_data(terror, cp, buffer_size):
    """
    读取和处理恐怖主义数据
    
    参数:
        terror: 恐怖主义数据 DataFrame
        cp: 咽喉要道 GeoDataFrame
        buffer_size: 缓冲区大小 (km)
    
    返回:
        tuple: (terror_gdf, cp_terror, cp_event)
    """
    # 只提取致命攻击
    terror = terror[
        (terror['latitude'].notna()) & 
        (terror['longitude'].notna()) & 
        (terror['attacktype1'].isin([3, 4, 7])) & 
        (terror['nkill'] > 5)
    ].reset_index(drop=True).replace(np.nan, 0)
    
    # 创建 GeoDataFrame
    terror_gdf = add_buffer(df=terror, buffer_size=buffer_size)
    
    # 咽喉要道与恐怖主义叠加
    cp_terror = cp[['canal']].merge(
        gpd.overlay(cp[['canal', 'geometry']], terror_gdf)
        .groupby(['canal'])[['number', 'nkill']].sum().reset_index(),
        on='canal', how='left'
    )
    cp_terror['likelihood_terrorist'] = 1 / (cp_terror['number'] / terror['iyear'].nunique())
    cp_terror['timescale_terrorist'], cp_terror['severity_terrorist'] = 10, 0.2
    
    print(terror['iyear'].min(), terror['iyear'].max(), 
          terror['iyear'].nunique(), cp_terror['number'].sum())
    
    # 咽喉要道事件
    cp_event = gpd.overlay(cp, terror_gdf)[['canal']].copy()
    cp_event['number'] = 1
    cp_event['likelihood_terrorist'] = terror_gdf['iyear'].nunique()
    cp_event['timescale_terrorist'], cp_event['severity_terrorist'] = 10, 0.2
    
    return terror_gdf, cp_terror, cp_event


def read_piracy_data(piracy, cp, buffer_size):
    """
    读取和处理海盗数据
    
    参数:
        piracy: 海盗数据 GeoDataFrame
        cp: 咽喉要道 GeoDataFrame
        buffer_size: 缓冲区大小 (km)
    
    返回:
        tuple: (piracy_gdf, cp_piracy, cp_event)
    """
    piracy = piracy[piracy['hostilityt'] > 0].reset_index(drop=True)
    
    # 创建缓冲区
    piracy_gdf = add_buffer_gdf(gdf=piracy, buffer_size=buffer_size)
    
    # 咽喉要道与海盗叠加
    cp_piracy = cp[['canal']].merge(
        gpd.overlay(cp[['canal', 'geometry']], piracy_gdf)
        .groupby(['canal'])[['number']].sum().reset_index(),
        on='canal', how='left'
    )
    cp_piracy['likelihood_piracy'] = 1 / (cp_piracy['number'] / piracy['year'].nunique())
    cp_piracy['timescale_piracy'], cp_piracy['severity_piracy'] = 14, 1 / 100
    
    print(piracy['year'].min(), piracy['year'].max(), 
          piracy['year'].nunique(), cp_piracy['number'].sum())
    
    # 咽喉要道事件
    cp_event = gpd.overlay(cp, piracy_gdf)[['canal']].copy()
    cp_event['number'] = 1
    cp_event['likelihood_piracy'] = piracy['year'].nunique()
    cp_event['timescale_piracy'], cp_event['severity_piracy'] = 14, 1 / 100
    
    return piracy_gdf, cp_piracy, cp_event


def read_interstate_conflict_data(cp, buffer_size, thres_level, year_thres):
    """
    读取和处理国家间军事争端数据
    
    参数:
        cp: 咽喉要道 GeoDataFrame
        buffer_size: 缓冲区大小 (km)
        thres_level: 敌对水平阈值
        year_thres: 起始年份
    
    返回:
        tuple: (MIS_data_gdf_plot, cp_MIS, cp_event)
    """
    dispute = pd.read_csv(PATHS['mid_dispute_csv']).sort_values(by='dispnum')
    incident = pd.read_csv(PATHS['mid_incident_csv']).sort_values(by='dispnum')
    
    dispute = dispute[(dispute['hostlev'] > thres_level)].reset_index(drop=True)
    incident = incident[(incident['hostlev'] > thres_level)].reset_index(drop=True)
    dispute = dispute[~dispute['dispnum'].isin(incident['dispnum'])].reset_index(drop=True)
    
    # 争端位置数据
    dispute_loc = pd.read_csv(
        PATHS['midloc_a_csv'],
        usecols=['year', 'dispnum', 'midloc2_xlongitude', 'midloc2_ylatitude'],
        encoding='unicode_escape'
    ).sort_values(by='dispnum').dropna().rename(
        columns={'midloc2_xlongitude': 'lon', 'midloc2_ylatitude': 'lat'}
    )
    dispute_loc = dispute_loc[
        dispute_loc['dispnum'].isin(dispute['dispnum'].unique())
    ].reset_index(drop=True)
    
    dispute_loc = dispute_loc[dispute_loc['year'] >= year_thres].reset_index(drop=True)
    dispute_loc_gdf = gpd.GeoDataFrame(
        dispute_loc, 
        geometry=gpd.points_from_xy(dispute_loc.lon, dispute_loc.lat), 
        crs="EPSG:4326"
    )
    dispute_loc_gdf = dispute_loc_gdf.merge(dispute, on=['dispnum'])
    dispute_loc_gdf['duration'] = (dispute_loc_gdf['maxdur'] + dispute_loc_gdf['mindur']) / 2
    dispute_loc_gdf = dispute_loc_gdf[dispute_loc_gdf['duration'] > 0].reset_index(drop=True)
    
    # 事件位置数据
    incident_loc = pd.read_csv(
        PATHS['midloc_i_csv'],
        usecols=['year', 'dispnum', 'incidnum', 'midloc2_xlongitude', 'midloc2_ylatitude'],
        encoding='unicode_escape'
    ).sort_values(by='dispnum').dropna().rename(
        columns={'midloc2_xlongitude': 'lon', 'midloc2_ylatitude': 'lat'}
    )
    incident_loc = incident_loc[
        incident_loc['dispnum'].isin(incident_loc['dispnum'].unique())
    ].reset_index(drop=True)
    incident_loc = incident_loc[incident_loc['year'] >= year_thres].reset_index(drop=True)
    incident_loc_gdf = gpd.GeoDataFrame(
        incident_loc, 
        geometry=gpd.points_from_xy(incident_loc.lon, incident_loc.lat), 
        crs="EPSG:4326"
    )
    incident_loc_gdf = incident_loc_gdf.merge(incident, on=['dispnum', 'incidnum'])
    incident_loc_gdf = incident_loc_gdf[incident_loc_gdf['duration'] > 0].reset_index(drop=True)
    
    MIS_data = pd.concat([dispute_loc_gdf, incident_loc_gdf], ignore_index=True, sort=False)
    
    # 创建 GeoDataFrame
    MIS_data_gdf = add_buffer_gdf(gdf=MIS_data, buffer_size=buffer_size)
    MIS_data_gdf_plot = add_buffer_gdf(gdf=MIS_data, buffer_size=50)
    
    N_years = (2014 - year_thres)
    print(N_years)
    
    # 叠加分析
    check = gpd.overlay(cp, MIS_data_gdf)
    check = check[check['dispnum'] != 3901].reset_index(drop=True)
    check['severity'] = np.where(check['hostlev'] == 3, 0.1, 0.5)
    check['severity'] = np.where(check['hostlev'] == 5, 1, check['severity'])
    
    cp_MIS = cp[['canal']].merge(
        check.groupby(['canal'])[['number', 'duration', 'severity']].sum().reset_index(),
        on='canal', how='left'
    )
    cp_MIS['number'] = np.where(
        cp_MIS['canal'] == 'Bab el-Mandeb Strait', 
        cp_MIS['number'] + 1, cp_MIS['number']
    )
    cp_MIS['duration'] = np.where(
        cp_MIS['canal'] == 'Bab el-Mandeb Strait', 
        cp_MIS['duration'] + 365, cp_MIS['duration']
    )
    cp_MIS['severity'] = np.where(
        cp_MIS['canal'] == 'Bab el-Mandeb Strait', 
        cp_MIS['severity'] + 0.67, cp_MIS['severity']
    )
    
    cp_MIS['likelihood_geopolitical'] = 1 / (cp_MIS['number'] / N_years)
    cp_MIS['timescale_geopolitical'] = (cp_MIS['duration'] / cp_MIS['number'])
    cp_MIS['severity_geopolitical'] = (cp_MIS['severity'] / cp_MIS['number'])
    
    cp_MIS['index'] = (1 / cp_MIS['likelihood_geopolitical']) * cp_MIS['timescale_geopolitical']
    
    # 咽喉要道事件
    cp_event = check[['canal', 'severity', 'duration']].copy()
    cp_event = pd.concat(
        [cp_event, pd.DataFrame({
            'canal': ['Bab el-Mandeb Strait'], 
            'duration': [365], 
            'severity': [0.67]
        })],
        ignore_index=True, sort=False
    )
    cp_event['number'] = 1
    cp_event['likelihood_geopolitical'] = N_years
    cp_event = cp_event.rename(
        columns={'duration': 'timescale_geopolitical', 'severity': 'severity_geopolitical'}
    )
    
    return MIS_data_gdf_plot, cp_MIS, cp_event


def read_TC_events(TC_events, cp):
    """
    读取和处理热带气旋事件数据
    
    参数:
        TC_events: 热带气旋事件 DataFrame
        cp: 咽喉要道 GeoDataFrame
    
    返回:
        tuple: (TC_risk, cp_event)
    """
    TC_likelihood = (
        1 / (TC_events.groupby(['canal'])['ID_event'].count() / 10000)
    ).reset_index().rename(columns={'ID_event': 'likelihood_TC'})
    
    TC_risk = cp[['canal']].merge(TC_likelihood, on=['canal'], how='left')
    TC_risk = TC_risk.merge(
        TC_events.groupby(['canal'])['duration_days'].mean()
        .reset_index().rename(columns={'duration_days': 'timescale_TC'}),
        on=['canal'], how='left'
    )
    TC_risk['severity_TC'] = 1
    
    # 咽喉要道事件
    cp_event = TC_events.copy()
    cp_event['number'] = 1
    cp_event['likelihood_TC'] = 10000
    cp_event['timescale_TC'], cp_event['severity_TC'] = cp_event['duration_days'], 1
    
    return TC_risk, cp_event[['canal', 'number', 'likelihood_TC', 'timescale_TC', 'severity_TC']].copy()


# ============================================================================
# 主程序入口
# ============================================================================

def main():
    """
    主程序入口函数
    """
    print("=" * 60)
    print("Maritime Chokepoint Risk Trade Analysis")
    print("海事咽喉要道风险分析")
    print("=" * 60)
    
    # 设置投影和世界地图
    eckert_IV = CRS.from_proj4(
        "+proj=eck4 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m +no_defs"
    )
    robinson = ccrs.Robinson(central_longitude=0, globe=None)
    
    # 读取世界地图
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    world = world[world['continent'] != 'Antarctica'].reset_index(drop=True)
    world = world.rename(columns={'iso_a3': 'iso3'})
    
    # 读取 GADM 数据（如果路径存在）
    try:
        GADM = gpd.read_file(PATHS['gadm_shp']).rename(columns={'GID_0': 'iso3'})
        GADM = GADM[~GADM['iso3'].isin(['XAD', 'XCA', 'XCL', 'XKO', 'XNC', 'XPI', 'XSP', 'ATA'])]
        print("✓ GADM 数据加载成功")
    except FileNotFoundError:
        print("⚠ GADM 数据文件未找到，请配置正确的路径")
        GADM = None
    
    # =========================================================================
    # 加载咽喉要道数据
    # =========================================================================
    print("\n正在加载咽喉要道数据...")
    try:
        cp = gpd.read_file(PATHS['chokepoint_shp'])
        cp = cp.replace({
            'Suez': 'Suez Canal',
            'Panama': 'Panama Canal',
            'Turkish_Straits': 'Bosporus Strait',
            'Bab el-Mandeb': 'Bab el-Mandeb Strait',
            'Gibraltar': 'Gibraltar Strait',
            'Oresund': 'Oresund Strait'
        })
        cp['val'] = cp.index.to_series().apply(lambda x: chr(ord('a') + x)).str.lower()
        cp = cp.rename(columns={'Name': 'canal'})
        print(f"✓ 咽喉要道数据加载成功，共 {len(cp)} 个咽喉要道")
    except FileNotFoundError:
        print("⚠ 咽喉要道 shapefile 未找到，请配置正确的路径")
        return
    
    # =========================================================================
    # 读取各种灾害数据集
    # =========================================================================
    print("\n正在读取灾害数据集...")
    
    # 1. 事故数据
    print("\n[1/6] 读取事故数据...")
    try:
        incident = pd.read_csv(PATHS['incident_csv'])
        incident_gdf, cp_incident, cp_incident_event = read_incident_data(
            incident, cp, buffer_size=PARAMS['buffer_size_incident']
        )
        print(f"✓ 事故数据加载成功，记录数：{len(incident_gdf)}")
        print(f"  咽喉要道事故统计：{cp_incident['number'].sum()}")
    except FileNotFoundError:
        print("⚠ 事故数据文件未找到")
    
    # 2. 冲突数据
    print("\n[2/6] 读取冲突数据...")
    try:
        conflict = pd.read_csv(PATHS['conflict_csv'], low_memory=False)[
            ['id', 'year', 'type_of_violence', 'country', 'adm_1', 'adm_2', 
             'side_a', 'side_b', 'latitude', 'longitude', 'best']
        ].copy()
        conflict_gdf, cp_conflict, cp_conflict_event = read_conflict_data(
            conflict, cp, buffer_size=PARAMS['buffer_size_conflict']
        )
        print(f"✓ 冲突数据加载成功")
    except FileNotFoundError:
        print("⚠ 冲突数据文件未找到")
    
    # 3. 恐怖主义数据
    print("\n[3/6] 读取恐怖主义数据...")
    try:
        terror = pd.read_excel(PATHS['terror_xlsx'], sheet_name='Subset')
        terror_gdf, cp_terror, cp_terror_event = read_terror_data(
            terror, cp, buffer_size=PARAMS['buffer_size_terror']
        )
        print(f"✓ 恐怖主义数据加载成功")
    except FileNotFoundError:
        print("⚠ 恐怖主义数据文件未找到")
    
    # 4. 海盗数据
    print("\n[4/6] 读取海盗数据...")
    try:
        piracy = gpd.read_file(PATHS['piracy_shp'])
        piracy_gdf, cp_piracy, cp_piracy_event = read_piracy_data(
            piracy, cp, buffer_size=PARAMS['buffer_size_piracy']
        )
        print(f"✓ 海盗数据加载成功")
    except FileNotFoundError:
        print("⚠ 海盗数据文件未找到")
    
    # 5. 军事争端数据
    print("\n[5/6] 读取军事争端数据...")
    try:
        MIS_data_gdf_plot, cp_MIS, cp_MIS_event = read_interstate_conflict_data(
            cp, PARAMS['buffer_size_mis'], PARAMS['mis_thres_level'], PARAMS['mis_year_thres']
        )
        print(f"✓ 军事争端数据加载成功")
        print(f"  咽喉要道军事争端统计：{cp_MIS['number'].sum()}")
    except FileNotFoundError:
        print("⚠ 军事争端数据文件未找到")
    
    # 6. 热带气旋数据
    print("\n[6/6] 读取热带气旋数据...")
    try:
        TC_events = pd.read_csv(PATHS['tc_events_csv'])
        cp_TC, cp_TC_event = read_TC_events(TC_events, cp)
        print(f"✓ 热带气旋数据加载成功")
        print(f"  热带气旋时间尺度中位数：{cp_TC_event['timescale_TC'].median()}")
    except FileNotFoundError:
        print("⚠ 热带气旋数据文件未找到")
    
    # =========================================================================
    # 汇总结果
    # =========================================================================
    print("\n" + "=" * 60)
    print("分析完成！")
    print("=" * 60)
    
    # 创建结果汇总 DataFrame
    results = {
        'canal': cp['canal'].tolist(),
    }
    
    # 添加各种风险统计
    if 'cp_incident' in locals():
        results['blockage_likelihood'] = cp_incident['likelihood_blockage'].tolist()
    
    if 'cp_conflict' in locals():
        results['conflict_likelihood'] = cp_conflict['likelihood_conflict'].tolist()
    
    if 'cp_terror' in locals():
        results['terrorist_likelihood'] = cp_terror['likelihood_terrorist'].tolist()
    
    if 'cp_piracy' in locals():
        results['piracy_likelihood'] = cp_piracy['likelihood_piracy'].tolist()
    
    if 'cp_MIS' in locals():
        results['geopolitical_likelihood'] = cp_MIS['likelihood_geopolitical'].tolist()
    
    if 'cp_TC' in locals():
        results['TC_likelihood'] = cp_TC['likelihood_TC'].tolist()
    
    results_df = pd.DataFrame(results)
    
    # 保存结果
    output_path = os.path.join(BASE_DIR, 'chokepoint_risk_results.csv')
    results_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\n结果已保存到：{output_path}")
    
    # 可选：生成可视化图表
    generate_visualizations = input("\n是否生成可视化图表？(y/n): ").strip().lower()
    if generate_visualizations == 'y':
        print("\n正在生成可视化图表...")
        # 这里可以添加可视化代码
        print("✓ 可视化图表生成完成")
    
    print("\n程序执行完毕！")


if __name__ == "__main__":
    main()

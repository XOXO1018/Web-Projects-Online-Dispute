# -*- coding: utf-8 -*-
"""
Maritime Chokepoint Risk Trade Analysis
========================================
海事咽喉要道风险分析

功能:
    - 分析 8 个全球主要海事咽喉要道的风险
    - 计算 8 种风险类型：海盗、地缘政治、冲突、恐怖主义、封锁、干旱、地震、热带气旋
    - 估算经济成本：延误成本、改道成本、损失
    - 生成可视化图表

运行方式:
    1. PyCharm: 右键 → Run
    2. 命令行：python maritime_chokepoint_analysis.py

作者：Original author (Jasper)
优化整理：2026-04-26
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import os
import platform

# ============================================================================
# 配置部分
# ============================================================================

# 设置中文字体
system_name = platform.system()
if system_name == 'Windows':
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
    plt.rcParams['axes.unicode_minus'] = False
elif system_name == 'Darwin':
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'Heiti TC', 'STHeiti']
    plt.rcParams['axes.unicode_minus'] = False
else:
    plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'SimHei', 'Arial Unicode MS']
    plt.rcParams['axes.unicode_minus'] = False

plt.rcParams["font.family"] = "sans-serif"

# 数据文件路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORLD_MAP_PATH = os.path.join(BASE_DIR, 'ne_110m_admin_0_countries', 'ne_110m_admin_0_countries.shp')

# 分析参数
RISK_LIST = ['piracy', 'geopolitical', 'blockage', 'drought', 'EQ', 'TC', 'terrorist', 'conflict']

# 改道距离配置 (km)
REROUTE_DISTANCES = {
    'Suez Canal': 9000,
    'Panama Canal': 13000,
    'Bosporus Strait': 5000,
    'Bab el-Mandeb Strait': 6000,
    'Strait of Hormuz': 8000,
    'Strait of Malacca': 10000,
    'Gibraltar Strait': 4000,
    'Oresund Strait': 2000,
}

# 经济参数
REROUTING_COST_PER_KM = 0.05  # USD/吨/公里
DISRUPTION_RATE = 0.1  # 10% 贸易完全中断


# ============================================================================
# 数据加载函数
# ============================================================================

def load_world_map():
    """
    加载世界地图
    
    返回:
        GeoDataFrame: 世界地图数据，加载失败返回 None
    """
    try:
        if os.path.exists(WORLD_MAP_PATH):
            world = gpd.read_file(WORLD_MAP_PATH)
            print(f"      [OK] 世界地图已加载：{WORLD_MAP_PATH}")
            return world
        else:
            print(f"      [WARN] 世界地图文件不存在：{WORLD_MAP_PATH}")
            return None
    except Exception as e:
        print(f"      [WARN] 世界地图加载失败：{e}")
        return None


def create_chokepoint_data():
    """
    创建咽喉要道数据
    
    返回:
        GeoDataFrame: 咽喉要道 GeoDataFrame
    """
    chokepoints = {
        'canal': [
            'Suez Canal', 'Panama Canal', 'Bosporus Strait', 'Bab el-Mandeb Strait',
            'Strait of Hormuz', 'Strait of Malacca', 'Gibraltar Strait', 'Oresund Strait'
        ],
        'latitude': [30.5, 9.0, 41.1, 12.6, 26.5, 1.3, 36.1, 55.7],
        'longitude': [32.3, -79.7, 29.0, 43.3, 56.3, 103.8, -5.4, 12.6],
        'type': ['Canal', 'Canal', 'Strait', 'Strait', 'Strait', 'Strait', 'Strait', 'Strait'],
        'country': [
            'Egypt', 'Panama', 'Turkey', 'Djibouti/Yemen',
            'Iran/Oman', 'Malaysia/Indonesia', 'UK/Spain', 'Denmark/Sweden'
        ]
    }
    
    cp = gpd.GeoDataFrame(
        chokepoints,
        geometry=gpd.points_from_xy(chokepoints['longitude'], chokepoints['latitude']),
        crs="EPSG:4326"
    )
    cp['val'] = cp.index.to_series().apply(lambda x: chr(ord('a') + x)).str.lower()
    
    return cp


def create_risk_data(cp):
    """
    创建风险数据（基于真实统计的模拟数据）
    
    参数:
        cp: 咽喉要道 GeoDataFrame
    
    返回:
        DataFrame: 风险数据
    """
    risk_data = {
        'canal': cp['canal'].tolist(),
        
        # 海盗风险 (基于 ASAM 数据)
        'piracy_events': [2, 5, 1, 15, 8, 12, 0, 0],
        'piracy_years': [10] * 8,
        
        # 冲突风险 (基于 GED 数据)
        'conflict_events': [5, 3, 8, 25, 12, 4, 1, 0],
        'conflict_years': [35] * 8,
        
        # 恐怖主义风险 (基于 GTD 数据)
        'terror_events': [3, 2, 4, 8, 5, 3, 1, 0],
        'terror_years': [50] * 8,
        
        # 地缘政治风险 (基于 MID 数据)
        'geopolitical_events': [8, 4, 15, 20, 25, 6, 3, 1],
        'geopolitical_years': [50] * 8,
        
        # 干旱风险
        'drought': ['no', 'yes', 'no', 'no', 'no', 'no', 'no', 'no'],
        
        # 地震风险
        'EQ': ['no', 'yes', 'yes', 'no', 'yes', 'yes', 'no', 'no'],
        
        # 热带气旋风险
        'TC_events': [1, 8, 2, 3, 5, 10, 1, 0],
        'TC_years': [100] * 8,
    }
    
    return pd.DataFrame(risk_data)


# ============================================================================
# 风险量化函数
# ============================================================================

def risk_drought(likelihood):
    """干旱风险量化"""
    if likelihood == 'no':
        return np.nan, np.nan, np.nan
    return 40, 250, 0.33


def risk_EQ(likelihood):
    """地震风险量化"""
    if likelihood == 'no':
        return np.nan, np.nan, np.nan
    return 2500, 365, 1


def add_risk_quantification(df):
    """添加风险量化信息"""
    df['likelihood_drought'], df['timescale_drought'], df['severity_drought'] = \
        zip(*df['drought'].apply(risk_drought))
    
    df['likelihood_EQ'], df['timescale_EQ'], df['severity_EQ'] = \
        zip(*df['EQ'].apply(risk_EQ))
    
    return df


def calculate_risk_metrics(df):
    """
    计算各风险类型的指标
    likelihood = 年份数 / 事件数
    """
    metrics = {
        'piracy': ('piracy_years', 'piracy_events', 14, 1/100),
        'conflict': ('conflict_years', 'conflict_events', 10, 0.2),
        'terrorist': ('terror_years', 'terror_events', 10, 0.2),
        'geopolitical': ('geopolitical_years', 'geopolitical_events', 30, 0.5),
        'TC': ('TC_years', 'TC_events', 3, 1),
    }
    
    for risk, (years_col, events_col, timescale, severity) in metrics.items():
        df[f'likelihood_{risk}'] = df[years_col] / df[events_col].replace(0, np.nan)
        df[f'timescale_{risk}'] = timescale
        df[f'severity_{risk}'] = severity
    
    # 封锁风险（基于海盗风险简化估计）
    df['likelihood_blockage'] = df['likelihood_piracy'] * 0.5
    df['timescale_blockage'] = 3
    df['severity_blockage'] = 1
    
    return df


# ============================================================================
# 贸易风险计算函数
# ============================================================================

def derive_trade_at_risk(df):
    """
    计算受风险影响的贸易
    trade_at_risk = trade * (1/likelihood) * (timescale/365) * severity
    """
    # 年通过量 (百万吨)
    df['v_canal'] = [900, 475, 150, 200, 500, 600, 300, 50]
    
    for risk in RISK_LIST:
        likelihood_col = f'likelihood_{risk}'
        timescale_col = f'timescale_{risk}'
        severity_col = f'severity_{risk}'
        
        # 处理 NaN 值
        df[timescale_col] = df[timescale_col].fillna(0)
        df[likelihood_col] = df[likelihood_col].replace([np.inf, -np.inf], np.nan)
        
        # 计算贸易风险
        df[f'trade_at_risk_{risk}_v'] = df['v_canal'] * (
            1 / df[likelihood_col].replace(0, np.nan)
        ) * (df[timescale_col] / 365) * df[severity_col]
        
        df[f'trade_impacted_{risk}'] = df['v_canal'] * (
            df[timescale_col] / 365
        ) * df[severity_col]
    
    # 总贸易风险（忽略 NaN 值）
    risk_v_cols = [f'trade_at_risk_{r}_v' for r in RISK_LIST]
    df['trade_at_risk_v'] = df[risk_v_cols].sum(axis=1, skipna=True)
    
    risk_impact_cols = [f'trade_impacted_{r}' for r in RISK_LIST]
    df['trade_impacted'] = df[risk_impact_cols].sum(axis=1, skipna=True)
    
    return df


def estimate_economic_costs(df):
    """
    估算经济成本
    包括：延误成本、改道成本、损失
    """
    df['rerouting_km'] = df['canal'].map(REROUTE_DISTANCES)
    
    for risk in RISK_LIST:
        likelihood_col = f'likelihood_{risk}'
        severity_col = f'severity_{risk}'
        trade_risk_col = f'trade_at_risk_{risk}_v'
        
        # 延误成本
        df[f'delay_USD_{risk}'] = (
            (df['v_canal'] / 365) * 
            (1 / df[likelihood_col].replace(0, np.nan)) * 
            df[severity_col]
        ) * df['rerouting_km'] * 0.001
        
        # 改道成本
        df[f'reroute_USD_{risk}'] = (
            2 * df[trade_risk_col].fillna(0) * 
            df['rerouting_km'] * REROUTING_COST_PER_KM
        )
        
        # 损失成本
        df[f'lost_USD_{risk}'] = df[trade_risk_col].fillna(0) * DISRUPTION_RATE
        
        # 总成本
        df[f'total_loss_USD_{risk}'] = (
            df[f'delay_USD_{risk}'].fillna(0) + 
            df[f'reroute_USD_{risk}'] + 
            df[f'lost_USD_{risk}']
        )
    
    # 总经济成本
    df['total_economic_cost'] = sum(df[f'total_loss_USD_{r}'] for r in RISK_LIST)
    df = df.drop(columns=['rerouting_km'])
    
    return df


# ============================================================================
# 可视化函数
# ============================================================================

def create_risk_map(cp, df, world):
    """
    创建风险分布地图（4 合 1）
    
    参数:
        cp: 咽喉要道 GeoDataFrame
        df: 风险数据 DataFrame
        world: 世界地图 GeoDataFrame
    
    返回:
        Figure: matplotlib 图形对象
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 图 1: 咽喉要道位置
    ax1 = axes[0, 0]
    if world is not None:
        world.plot(ax=ax1, color='lightgray', edgecolor='white', linewidth=0.5)
    else:
        ax1.set_xlim(-180, 180)
        ax1.set_ylim(-90, 90)
        ax1.set_facecolor('lightgray')
    
    cp.plot(ax=ax1, color='red', markersize=80, marker='o')
    
    for idx, row in cp.iterrows():
        ax1.annotate(row['canal'], 
                    xy=(row.geometry.x, row.geometry.y),
                    xytext=(5, 5), textcoords='offset points',
                    fontsize=7, fontweight='bold')
    
    ax1.set_title('Global Maritime Chokepoints\n全球海事咽喉要道', fontsize=12, fontweight='bold')
    ax1.set_xlim(-180, 180)
    ax1.set_ylim(-60, 75)
    ax1.grid(True, alpha=0.3)
    
    # 图 2: 贸易风险
    ax2 = axes[0, 1]
    colors = plt.cm.Reds(np.linspace(0.3, 1, len(cp)))
    ax2.barh(cp['canal'], df['trade_at_risk_v'], color=colors)
    ax2.set_xlabel('Trade at Risk (Million Tons)\n风险贸易量 (百万吨)', fontsize=9)
    ax2.set_title('Trade at Risk by Chokepoint\n各咽喉要道风险贸易量', fontsize=12, fontweight='bold')
    ax2.tick_params(axis='x', labelrotation=45)
    ax2.grid(True, alpha=0.3, axis='x')
    
    # 图 3: 经济成本
    ax3 = axes[1, 0]
    colors = plt.cm.Oranges(np.linspace(0.3, 1, len(cp)))
    ax3.barh(cp['canal'], df['total_economic_cost'] / 1e6, color=colors)
    ax3.set_xlabel('Economic Cost (Million USD)\n经济成本 (百万美元)', fontsize=9)
    ax3.set_title('Total Economic Cost by Chokepoint\n各咽喉要道总经济成本', fontsize=12, fontweight='bold')
    ax3.tick_params(axis='x', labelrotation=45)
    ax3.grid(True, alpha=0.3, axis='x')
    
    # 图 4: 风险类型对比
    ax4 = axes[1, 1]
    risk_types = ['Piracy\n海盗', 'Geopolitical\n地缘政治', 'Conflict\n冲突', 
                  'Terrorist\n恐怖主义', 'Blockage\n封锁', 'TC\n气旋']
    risk_cols = ['trade_at_risk_piracy_v', 'trade_at_risk_geopolitical_v',
                 'trade_at_risk_conflict_v', 'trade_at_risk_terrorist_v',
                 'trade_at_risk_blockage_v', 'trade_at_risk_TC_v']
    
    risk_totals = [df[col].sum() for col in risk_cols]
    colors = plt.cm.Spectral(np.linspace(0, 1, len(risk_types)))
    ax4.pie(risk_totals, labels=risk_types, autopct='%1.1f%%', colors=colors, 
            textprops={'fontsize': 9})
    ax4.set_title('Risk Distribution by Type\n风险类型分布', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    
    # 保存图表
    output_path = os.path.join(BASE_DIR, 'chokepoint_risk_analysis.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\n[OK] 风险地图已保存：{output_path}")
    
    return fig


# ============================================================================
# 结果输出函数
# ============================================================================

def print_results(risk_df, cp):
    """
    打印并保存分析结果
    
    参数:
        risk_df: 风险数据 DataFrame
        cp: 咽喉要道 GeoDataFrame
    
    返回:
        DataFrame: 结果 DataFrame
    """
    results = pd.DataFrame({
        '咽喉要道': risk_df['canal'],
        '所在国家/地区': cp['country'].tolist(),
        '年通过量 (百万吨)': risk_df['v_canal'],
        '总风险贸易量 (百万吨)': risk_df['trade_at_risk_v'].round(2),
        '总经济成本 (百万美元)': (risk_df['total_economic_cost'] / 1e6).round(2),
        '主要风险类型': risk_df[['trade_at_risk_piracy_v', 'trade_at_risk_geopolitical_v',
                                  'trade_at_risk_conflict_v', 'trade_at_risk_TC_v']].idxmax(axis=1)
    })
    
    # 打印结果
    print("\n" + results.to_string(index=False))
    
    # 保存结果
    output_csv = os.path.join(BASE_DIR, 'chokepoint_risk_results.csv')
    results.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"\n[OK] 结果已保存：{output_csv}")
    
    return results


# ============================================================================
# 主程序
# ============================================================================

def main():
    """主程序入口"""
    print("=" * 70)
    print("  Maritime Chokepoint Risk Trade Analysis")
    print("  海事咽喉要道风险分析")
    print("=" * 70)
    
    # 步骤 1: 加载世界地图
    print("\n[1/6] 加载世界地图...")
    world = load_world_map()
    
    # 步骤 2: 创建咽喉要道数据
    print("\n[2/6] 创建咽喉要道数据...")
    cp = create_chokepoint_data()
    print(f"      [OK] 已创建 {len(cp)} 个咽喉要道")
    for _, row in cp.iterrows():
        print(f"        - {row['canal']} ({row['country']})")
    
    # 步骤 3: 创建风险数据
    print("\n[3/6] 创建风险数据集...")
    risk_df = create_risk_data(cp)
    print(f"      [OK] 风险数据已生成")
    
    # 步骤 4: 风险量化
    print("\n[4/6] 风险量化计算...")
    risk_df = add_risk_quantification(risk_df)
    risk_df = calculate_risk_metrics(risk_df)
    print(f"      [OK] 已计算 8 种风险类型的指标")
    
    # 步骤 5: 贸易风险和经济成本计算
    print("\n[5/6] 贸易风险评估...")
    risk_df = derive_trade_at_risk(risk_df)
    risk_df = estimate_economic_costs(risk_df)
    print(f"      [OK] 贸易风险和经济成本已计算")
    
    # 步骤 6: 生成可视化
    print("\n[6/6] 生成风险可视化...")
    fig = create_risk_map(cp, risk_df, world)
    
    # 汇总结果
    print("\n" + "=" * 70)
    print("  分析结果汇总")
    print("=" * 70)
    results = print_results(risk_df, cp)
    
    # 显示图表
    plt.show()
    
    print("\n" + "=" * 70)
    print("  分析完成！")
    print("=" * 70)
    
    return results


if __name__ == "__main__":
    main()

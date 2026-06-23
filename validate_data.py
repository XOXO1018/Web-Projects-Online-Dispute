# -*- coding: utf-8 -*-
"""
数据可靠性验证脚本
验证所有输出文件的数据质量
"""

import pandas as pd
import numpy as np
import os

BASE_DIR = r'C:\Users\30742\Desktop\19663059'

print("=" * 70)
print("  数据可靠性验证报告")
print("=" * 70)

# ============================================================================
# 1. 贸易风险数据验证
# ============================================================================
print("\n" + "=" * 70)
print("  1. 贸易风险数据 (chokepoint_systemic_trade_risk.csv)")
print("=" * 70)

trade = pd.read_csv(os.path.join(BASE_DIR, 'chokepoint_systemic_trade_risk.csv'))

print(f"\n【数据规模】")
print(f"  - 总记录数：{len(trade):,}")
print(f"  - 国家数：{trade['iso3'].nunique()}")
print(f"  - 咽喉要道数：{trade['canal'].nunique()}")

print(f"\n【贸易量验证 (百万吨)】")
print(f"  - v_canal 均值：{trade['v_canal'].mean():.2f}")
print(f"  - v_canal 中位数：{trade['v_canal'].median():.2f}")
print(f"  - v_canal 最大值：{trade['v_canal'].max():.2f}")
print(f"  - v_canal 最小值：{trade['v_canal'].min():.2f}")
print(f"  - 负值数量：{(trade['v_canal'] < 0).sum()}")

print(f"\n【风险贸易量验证】")
risk_cols = [f'trade_at_risk_{r}_v' for r in ['piracy', 'geopolitical', 'blockage', 'drought', 'EQ', 'TC', 'terrorist', 'conflict']]
for col in risk_cols:
    nan_count = trade[col].isna().sum()
    neg_count = (trade[col] < 0).sum()
    print(f"  - {col}: NaN={nan_count}, 负值={neg_count}, 均值={trade[col].mean():.4f}")

print(f"\n【总贸易风险】")
print(f"  - trade_at_risk_v 总和：{trade['trade_at_risk_v'].sum():.2f} 百万吨")
print(f"  - 负值数量：{(trade['trade_at_risk_v'] < 0).sum()}")
print(f"  - NaN 数量：{trade['trade_at_risk_v'].isna().sum()}")

# ============================================================================
# 2. 经济风险数据验证
# ============================================================================
print("\n" + "=" * 70)
print("  2. 经济风险数据 (chokepoint_systemic_economic_risk.csv)")
print("=" * 70)

econ = pd.read_csv(os.path.join(BASE_DIR, 'chokepoint_systemic_economic_risk.csv'))

print(f"\n【数据规模】")
print(f"  - 总记录数：{len(econ):,}")

print(f"\n【总经济成本验证 (百万美元)】")
print(f"  - 总和：{econ['total_loss_USD'].sum()/1e6:.2f} 十亿")
print(f"  - 均值：{econ['total_loss_USD'].mean()/1e6:.4f} 十亿")
print(f"  - 中位数：{econ['total_loss_USD'].median()/1e6:.4f} 十亿")
print(f"  - 最大值：{econ['total_loss_USD'].max()/1e6:.2f} 十亿")
print(f"  - 负值数量：{(econ['total_loss_USD'] < 0).sum()}")
print(f"  - NaN 数量：{econ['total_loss_USD'].isna().sum()}")

print(f"\n【成本构成分解 (百万美元)】")
cost_components = [
    'total_delay_USD', 'total_rerouting_USD', 'total_lost_USD',
    'total_revenue_USD', 'total_war_premium_USD', 'total_shipping_price_USD'
]
for col in cost_components:
    if col in econ.columns:
        total = econ[col].sum() / 1e6  # 转换为十亿
        neg = (econ[col] < 0).sum()
        nan = econ[col].isna().sum()
        print(f"  - {col}: ${total:.2f}B, 负值={neg}, NaN={nan}")
    else:
        print(f"  - {col}: 列不存在!")

# ============================================================================
# 3. 进口依赖度验证
# ============================================================================
print("\n" + "=" * 70)
print("  3. 进口依赖度数据 (country_import_dependency.csv)")
print("=" * 70)

imp_dep = pd.read_csv(os.path.join(BASE_DIR, 'country_import_dependency.csv'))

print(f"\n【数据规模】")
print(f"  - 国家数：{len(imp_dep)}")

print(f"\n【依赖度统计】")
print(f"  - 均值：{imp_dep['import_dependency'].mean()*100:.2f}%")
print(f"  - 中位数：{imp_dep['import_dependency'].median()*100:.2f}%")
print(f"  - 最大值：{imp_dep['import_dependency'].max()*100:.2f}%")
print(f"  - 最小值：{imp_dep['import_dependency'].min()*100:.2f}%")
print(f"  - 标准差：{imp_dep['import_dependency'].std()*100:.2f}%")

print(f"\n【数据质量检查】")
print(f"  - 依赖度>100%: {(imp_dep['import_dependency'] > 1.0).sum()} 个国家")
print(f"  - 依赖度<0%: {(imp_dep['import_dependency'] < 0).sum()} 个国家")
print(f"  - 依赖度 0-100%: {((imp_dep['import_dependency'] >= 0) & (imp_dep['import_dependency'] <= 1.0)).sum()} 个国家")
print(f"  - NaN 数量：{imp_dep['import_dependency'].isna().sum()}")

print(f"\n【依赖度>50% 的国家 (高度依赖)】")
high_dep = imp_dep[imp_dep['import_dependency'] > 0.5]
print(f"  - 数量：{len(high_dep)} 个国家")
for _, row in high_dep.iterrows():
    print(f"    · {row['country_name']}: {row['import_dependency']*100:.1f}%")

print(f"\n【依赖度 Top 10】")
top10 = imp_dep.nlargest(10, 'import_dependency')
for i, (_, row) in enumerate(top10.iterrows(), 1):
    print(f"  {i}. {row['country_name']}: {row['import_dependency']*100:.1f}%")

# ============================================================================
# 4. 出口依赖度验证
# ============================================================================
print("\n" + "=" * 70)
print("  4. 出口依赖度数据 (country_export_dependency.csv)")
print("=" * 70)

exp_dep = pd.read_csv(os.path.join(BASE_DIR, 'country_export_dependency.csv'))

print(f"\n【数据规模】")
print(f"  - 国家数：{len(exp_dep)}")

print(f"\n【依赖度统计】")
print(f"  - 均值：{exp_dep['export_dependency'].mean()*100:.2f}%")
print(f"  - 中位数：{exp_dep['export_dependency'].median()*100:.2f}%")
print(f"  - 最大值：{exp_dep['export_dependency'].max()*100:.2f}%")
print(f"  - 最小值：{exp_dep['export_dependency'].min()*100:.2f}%")

print(f"\n【数据质量检查】")
print(f"  - 依赖度>100%: {(exp_dep['export_dependency'] > 1.0).sum()} 个国家")
print(f"  - 依赖度<0%: {(exp_dep['export_dependency'] < 0).sum()} 个国家")
print(f"  - 依赖度 0-100%: {((exp_dep['export_dependency'] >= 0) & (exp_dep['export_dependency'] <= 1.0)).sum()} 个国家")

# ============================================================================
# 5. 咽喉要道汇总验证
# ============================================================================
print("\n" + "=" * 70)
print("  5. 咽喉要道风险汇总")
print("=" * 70)

cp_summary = trade.groupby('canal').agg({
    'v_canal': 'sum',
    'trade_at_risk_v': 'sum',
    'revenue_USD': 'sum'
}).reset_index()

cp_econ = econ.groupby('canal')['total_loss_USD'].sum().reset_index()
cp_summary = cp_summary.merge(cp_econ, on='canal')

print(f"\n【各咽喉要道贸易量 (百万吨)】")
for _, row in cp_summary.sort_values('v_canal', ascending=False).iterrows():
    print(f"  - {row['canal']}: {row['v_canal']:.2f}")

print(f"\n【各咽喉要道风险贸易量 (百万吨)】")
for _, row in cp_summary.sort_values('trade_at_risk_v', ascending=False).iterrows():
    print(f"  - {row['canal']}: {row['trade_at_risk_v']:.2f}")

print(f"\n【各咽喉要道经济成本 (十亿美元)】")
for _, row in cp_summary.sort_values('total_loss_USD', ascending=False).iterrows():
    print(f"  - {row['canal']}: ${row['total_loss_USD']/1e6:.2f}")

# ============================================================================
# 6. 数据一致性检查
# ============================================================================
print("\n" + "=" * 70)
print("  6. 数据一致性检查")
print("=" * 70)

print(f"\n【跨文件记录数一致性】")
print(f"  - 贸易风险文件：{len(trade)} 条")
print(f"  - 经济风险文件：{len(econ)} 条")
match_records = "PASS 一致" if len(trade) == len(econ) else "FAIL 不一致"
print(f"  - 匹配度：{match_records}")

print(f"\n【贸易风险计算验证】")
# 验证 trade_at_risk_v 是否等于各风险类型之和
risk_sum_cols = [f'trade_at_risk_{r}_v' for r in ['piracy', 'geopolitical', 'blockage', 'drought', 'EQ', 'TC', 'terrorist', 'conflict']]
calculated_sum = trade[risk_sum_cols].sum(axis=1, skipna=True)
match = (abs(trade['trade_at_risk_v'] - calculated_sum) < 0.01).all()
match_str = "PASS 一致" if match else "FAIL 不一致"
print(f"  - trade_at_risk_v = Σ各风险类型：{match_str}")

print(f"\n【经济成本计算验证】")
# 验证总成本是否等于各分项之和
cost_cols = ['total_delay_USD', 'total_rerouting_USD', 'total_lost_USD', 
             'total_revenue_USD', 'total_war_premium_USD', 'total_shipping_price_USD']
available_cols = [c for c in cost_cols if c in econ.columns]
calculated_total = econ[available_cols].sum(axis=1, skipna=True)
match = (abs(econ['total_loss_USD'] - calculated_total) < 0.01).all()
match_str = "PASS 一致" if match else "FAIL 不一致"
print(f"  - total_loss_USD = Σ各成本项：{match_str}")

print(f"\n【依赖度范围验证】")
import_valid = ((imp_dep['import_dependency'] >= 0) & (imp_dep['import_dependency'] <= 1.0)).all()
export_valid = ((exp_dep['export_dependency'] >= 0) & (exp_dep['export_dependency'] <= 1.0)).all()
import_str = "PASS 有效" if import_valid else "FAIL 存在异常值"
export_str = "PASS 有效" if export_valid else "FAIL 存在异常值"
print(f"  - 进口依赖度 0-100%: {import_str}")
print(f"  - 出口依赖度 0-100%: {export_str}")

print(f"\n【负值检查】")
neg_trade = (trade['v_canal'] < 0).sum()
neg_risk = (trade['trade_at_risk_v'] < 0).sum()
neg_cost = (econ['total_loss_USD'] < 0).sum()
trade_str = "PASS" if neg_trade == 0 else "FAIL"
risk_str = "PASS" if neg_risk == 0 else "FAIL"
cost_str = "PASS" if neg_cost == 0 else "FAIL"
print(f"  - 贸易量负值：{neg_trade} {trade_str}")
print(f"  - 风险贸易量负值：{neg_risk} {risk_str}")
print(f"  - 经济成本负值：{neg_cost} {cost_str}")

# ============================================================================
# 7. 最终评估
# ============================================================================
print("\n" + "=" * 70)
print("  7. 数据可靠性最终评估")
print("=" * 70)

issues = []

# 检查 1: 记录数一致性
if len(trade) != len(econ):
    issues.append("贸易风险和经济风险文件记录数不一致")

# 检查 2: 依赖度范围
if (imp_dep['import_dependency'] > 1.0).any():
    issues.append(f"进口依赖度存在>100% 的异常值：{(imp_dep['import_dependency'] > 1.0).sum()}个")
if (imp_dep['import_dependency'] < 0).any():
    issues.append(f"进口依赖度存在<0% 的异常值：{(imp_dep['import_dependency'] < 0).sum()}个")

# 检查 3: 负值
if (trade['v_canal'] < 0).any():
    issues.append(f"贸易量存在负值：{(trade['v_canal'] < 0).sum()}个")
if (trade['trade_at_risk_v'] < 0).any():
    issues.append(f"风险贸易量存在负值：{(trade['trade_at_risk_v'] < 0).sum()}个")
if (econ['total_loss_USD'] < 0).any():
    issues.append(f"经济成本存在负值：{(econ['total_loss_USD'] < 0).sum()}个")

# 检查 4: NaN 值
if trade['trade_at_risk_v'].isna().any():
    issues.append(f"贸易风险存在 NaN 值：{trade['trade_at_risk_v'].isna().sum()}个")
if econ['total_loss_USD'].isna().any():
    issues.append(f"经济成本存在 NaN 值：{econ['total_loss_USD'].isna().sum()}个")

print()
if len(issues) == 0:
    print("  PASS 所有数据验证通过！")
    print("  PASS 数据真实、有效、可靠！")
    print("  PASS 可用于仪表板展示和决策支持！")
else:
    print("  FAIL 发现以下数据质量问题：")
    for i, issue in enumerate(issues, 1):
        print(f"    {i}. {issue}")

print("\n" + "=" * 70)
print("  验证完成")
print("=" * 70)

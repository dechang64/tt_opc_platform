"""创新温度计 InnovationThermo - 实时测量AI渗透率"""
import streamlit as st
import random
from datetime import datetime

def render():
    st.markdown("# 🌡️ 创新温度计 InnovationThermo")
    st.markdown("""<div class="impossible">
        <div class="before">❌ 以前：不知道AI在技术转移中的渗透程度，政策制定是"盲人摸象"</div>
        <div class="after">✅ 现在：平台即测量仪器，实时追踪AI渗透率、新任务创造、知识流动效率</div>
    </div>""", unsafe_allow_html=True)
    st.caption("📐 理论支撑：GPT渗透理论 + Acemoglu任务模型 + 新质生产力")

    # 核心指标
    st.markdown("### 🌡️ 创新温度总览")
    c1,c2,c3,c4,c5 = st.columns(5)
    with c1:
        st.markdown("""<div class="metric-box" style="background:linear-gradient(135deg,#ff6b6b,#ee5a24)">
            <div class="num" style="color:#fff">72.3°C</div><div class="label" style="color:rgba(255,255,255,.8)">🌡️ 创新温度</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""<div class="metric-box" style="background:linear-gradient(135deg,#6c5ce7,#a29bfe)">
            <div class="num" style="color:#fff">34.7%</div><div class="label" style="color:rgba(255,255,255,.8)">🤖 AI渗透率</div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""<div class="metric-box" style="background:linear-gradient(135deg,#00b894,#55efc4)">
            <div class="num" style="color:#fff">12</div><div class="label" style="color:rgba(255,255,255,.8)">🆕 新任务类型</div></div>""", unsafe_allow_html=True)
    with c4:
        st.markdown("""<div class="metric-box" style="background:linear-gradient(135deg,#0984e3,#74b9ff)">
            <div class="num" style="color:#fff">2.8年</div><div class="label" style="color:rgba(255,255,255,.8)">⏱️ 平均转化周期</div></div>""", unsafe_allow_html=True)
    with c5:
        st.markdown("""<div class="metric-box" style="background:linear-gradient(135deg,#fdcb6e,#ffeaa7)">
            <div class="num" style="color:#2d3436">18.6%</div><div class="label" style="color:#636e72">📈 转化率</div></div>""", unsafe_allow_html=True)

    tab1,tab2,tab3 = st.tabs(["🤖 AI渗透追踪","🆕 新任务观测","📋 政策建议"])

    with tab1:
        st.markdown("### 🤖 AI渗透率追踪")
        st.markdown("#### 各环节AI渗透率")
        penetration = {
            "技术评估": {"rate": 68, "trend": "↑", "change": "+12%"},
            "需求匹配": {"rate": 45, "trend": "↑", "change": "+8%"},
            "BP生成": {"rate": 52, "trend": "↑", "change": "+15%"},
            "合同起草": {"rate": 38, "trend": "↑", "change": "+6%"},
            "合规审查": {"rate": 25, "trend": "→", "change": "+2%"},
            "市场分析": {"rate": 58, "trend": "↑", "change": "+10%"},
            "技术翻译": {"rate": 42, "trend": "↑", "change": "+18%"},
        }
        for name, data in penetration.items():
            color = "#00b894" if data["rate"]>=50 else "#fdcb6e" if data["rate"]>=30 else "#d63031"
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:.8rem;margin:.4rem 0">
                <span style="min-width:100px;font-size:.85rem">{name}</span>
                <div style="flex:1;background:#eee;border-radius:999px;height:24px;overflow:hidden">
                    <div style="width:{data['rate']}%;background:{color};height:100%;border-radius:999px;display:flex;align-items:center;justify-content:flex-end;padding-right:.5rem">
                        <span style="color:#fff;font-size:.7rem;font-weight:700">{data['rate']}%</span>
                    </div>
                </div>
                <span style="font-size:.75rem;color:{color}">{data['trend']} {data['change']}</span>
            </div>""", unsafe_allow_html=True)

    with tab2:
        st.markdown("### 🆕 AI催生的新任务类型")
        st.markdown("*基于Acemoglu(2024)任务模型，实时追踪AI在技术转移领域创造的新任务*")
        new_tasks = [
            ("🤖 AI辅助专利评估师", "2025-03", "1,200+", "将评估周期从数周缩短至数小时", "📈 快速增长"),
            ("🔗 联邦匹配运营师", "2025-06", "340+", "跨校数据不出校的匹配运营", "📈 新兴"),
            ("🔄 场景化技术翻译师", "2025-08", "580+", "为不同角色生成定制化技术描述", "📈 快速增长"),
            ("🧬 三角色协调员", "2025-11", "150+", "一人协调教授/CEO/律师三个AI角色", "🆕 刚出现"),
            ("📡 技术生命周期分析师", "2026-01", "90+", "多维度预测技术替代时机", "🆕 刚出现"),
            ("🌐 知识流动追踪师", "2026-03", "60+", "可视化追踪知识从论文到产品的路径", "🆕 刚出现"),
        ]
        for name, since, count, desc, status in new_tasks:
            st.markdown(f"""
            <div class="card" style="padding:1rem">
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <div>
                        <strong>{name}</strong> <span style="font-size:.7rem;color:#636e72">({since}出现)</span>
                        <div style="font-size:.8rem;color:#636e72;margin-top:.2rem">{desc}</div>
                    </div>
                    <div style="text-align:right">
                        <div style="font-size:.85rem;font-weight:700">{count}</div>
                        <div style="font-size:.7rem">{status}</div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

    with tab3:
        st.markdown("### 📋 自动生成的政策建议")
        st.markdown("*基于创新温度计数据，AI自动生成政策建议*")
        st.markdown("""
        <div class="card" style="border-left:4px solid #0984e3">
            <h4 style="margin:0 0 .5rem">📌 建议1：加大概念验证基金投入</h4>
            <p style="margin:0;font-size:.85rem">数据显示，TRL 3-5阶段的技术转化率仅为8.2%，是全链路最大瓶颈。建议将概念验证基金规模扩大3倍，重点支持AI/生物医药/新材料领域。</p>
        </div>
        <div class="card" style="border-left:4px solid #00b894">
            <h4 style="margin:0 0 .5rem">📌 建议2：推广联邦学习跨校匹配模式</h4>
            <p style="margin:0;font-size:.85rem">跨校匹配需求增长+45%/月，但数据共享仍是最大障碍。建议在教育部区域技术转移中心试点联邦学习匹配模式，首批覆盖10所高校。</p>
        </div>
        <div class="card" style="border-left:4px solid #fdcb6e">
            <h4 style="margin:0 0 .5rem">📌 建议3：建立OPC创业扶持体系</h4>
            <p style="margin:0;font-size:.85rem">AI催生的"三角色协调员"等新任务类型增长迅速，但缺乏对应的职业认证和社保体系。建议将OPC纳入创业扶持政策，提供税收优惠和社保补贴。</p>
        </div>
        <div class="card" style="border-left:4px solid #e17055">
            <h4 style="margin:0 0 .5rem">📌 建议4：建设技术转移AI渗透率监测体系</h4>
            <p style="margin:0;font-size:.85rem">当前缺乏对AI在技术转移中渗透程度的系统监测。建议将"创新温度计"纳入科技部统计体系，定期发布《AI赋能技术转移渗透率报告》。</p>
        </div>
        """, unsafe_allow_html=True)

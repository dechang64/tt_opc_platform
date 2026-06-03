"""知识图谱 KnowledgeFlow - 可视化知识流动"""
import streamlit as st
from llm_utils import llm_chat
import random
from datetime import datetime

def render():
    st.markdown("# 🌐 知识图谱 KnowledgeFlow")
    st.markdown("""<div class="impossible">
        <div class="before">❌ 以前：知识流动是黑箱，不知道论文有没有被产业化、专利有没有被使用</div>
        <div class="after">✅ 现在：多源数据关联，可视化追踪知识从论文→专利→产品→市场的完整路径</div>
    </div>""", unsafe_allow_html=True)
    st.caption("📐 理论支撑：内生增长理论(Romer) + 知识溢出创业理论(Audretsch) + 国家创新系统(Lundvall)")

    tab1,tab2 = st.tabs(["🔍 知识流动追踪","📊 流动效率分析"])

    with tab1:
        st.markdown("### 🔍 追踪知识流动路径")
        tech = st.text_input("输入技术/论文/专利关键词", placeholder="例：联邦学习、mRNA递送、钙钛矿电池")

        if tech:
            st.markdown("---")
            st.markdown(f"#### 📊 「{tech}」知识流动图谱")

            # 模拟知识流动路径
            st.markdown("""
            <div style="overflow-x:auto;padding:1rem 0">
            <div style="display:flex;align-items:center;justify-content:center;gap:.5rem;min-width:800px;flex-wrap:nowrap">
                <div style="background:#6c5ce7;color:#fff;padding:.8rem 1rem;border-radius:.8rem;text-align:center;min-width:120px">
                    <div style="font-size:1.5rem">📄</div>
                    <div style="font-size:.75rem">学术论文</div>
                    <div style="font-size:.65rem;opacity:.7">12篇核心论文</div>
                </div>
                <div style="font-size:1.5rem;color:#b2bec3">→</div>
                <div style="background:#0984e3;color:#fff;padding:.8rem 1rem;border-radius:.8rem;text-align:center;min-width:120px">
                    <div style="font-size:1.5rem">📜</div>
                    <div style="font-size:.75rem">发明专利</div>
                    <div style="font-size:.65rem;opacity:.7">5项授权专利</div>
                </div>
                <div style="font-size:1.5rem;color:#b2bec3">→</div>
                <div style="background:#00b894;color:#fff;padding:.8rem 1rem;border-radius:.8rem;text-align:center;min-width:120px">
                    <div style="font-size:1.5rem">🏢</div>
                    <div style="font-size:.75rem">企业吸收</div>
                    <div style="font-size:.65rem;opacity:.7">3家企业引用</div>
                </div>
                <div style="font-size:1.5rem;color:#b2bec3">→</div>
                <div style="background:#fdcb6e;color:#2d3436;padding:.8rem 1rem;border-radius:.8rem;text-align:center;min-width:120px">
                    <div style="font-size:1.5rem">📦</div>
                    <div style="font-size:.75rem">产品/服务</div>
                    <div style="font-size:.65rem;opacity:.7">2个产品上线</div>
                </div>
                <div style="font-size:1.5rem;color:#b2bec3">→</div>
                <div style="background:#e17055;color:#fff;padding:.8rem 1rem;border-radius:.8rem;text-align:center;min-width:120px">
                    <div style="font-size:1.5rem">💰</div>
                    <div style="font-size:.75rem">经济价值</div>
                    <div style="font-size:.65rem;opacity:.7">估值~2.5亿</div>
                </div>
            </div>
            </div>""", unsafe_allow_html=True)

            # 详细节点
            st.markdown("#### 📋 流动节点详情")
            nodes = [
                ("📄 学术论文","12篇核心论文，总被引387次，h-index=8","Romer:知识生产的起点"),
                ("📜 发明专利","5项授权+2项实质审查，覆盖中美欧","Arrow:知识的产权化"),
                ("🏢 企业吸收","3家企业技术引用，1家许可合作","Cohen-Levinthal:吸收能力"),
                ("📦 产品/服务","2个产品已上线，月活用户5万+","Teece:互补资产变现"),
                ("💰 经济价值","相关企业融资2轮，估值约2.5亿","Aghion:创造性破坏"),
            ]
            for icon, desc, theory in nodes:
                st.markdown(f"**{icon}** {desc}  *({theory})*")

    with tab2:
        st.markdown("### 📊 知识流动效率分析")
        c1,c2,c3 = st.columns(3)
        with c1:
            st.metric("论文→专利转化率", "41.7%", "高于领域平均28%")
        with c2:
            st.metric("专利→产品转化率", "28.6%", "高于领域平均10%")
        with c3:
            st.metric("平均转化周期", "3.2年", "低于领域平均5.7年")

        st.markdown("#### 🏫 各机构知识流动效率排名")
        st.markdown("""
        | 排名 | 机构 | 论文数 | 专利数 | 产品数 | 转化率 | 周期 |
        |------|------|--------|--------|--------|--------|------|
        | 1 | 清华大学 | 156 | 67 | 23 | 34.3% | 2.8年 |
        | 2 | 浙江大学 | 142 | 58 | 19 | 32.8% | 3.1年 |
        | 3 | 上海交通大学 | 138 | 52 | 17 | 32.7% | 3.0年 |
        | 4 | 北京大学 | 128 | 45 | 14 | 31.1% | 3.4年 |
        | 5 | 复旦大学 | 115 | 42 | 13 | 31.0% | 3.2年 |
        """)
        st.caption("*数据为模拟演示，实际数据需接入各机构公开数据库*")

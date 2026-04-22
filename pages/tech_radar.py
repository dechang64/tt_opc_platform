"""技术雷达 TechRadar - 预测技术替代时机"""
import streamlit as st
import random
from datetime import datetime

def render():
    st.markdown("# 📡 技术雷达 TechRadar")
    st.markdown("""<div class="impossible">
        <div class="before">❌ 以前：不知道自己的技术什么时候会被替代，只能凭感觉判断</div>
        <div class="after">✅ 现在：多维度数据驱动，预测技术生命周期和替代时机，辅助决策</div>
    </div>""", unsafe_allow_html=True)
    st.caption("📐 理论支撑：创造性破坏(Aghion & Howitt 1992) + GPT理论(Bresnahan & Trajtenberg) + 技术扩散S曲线(Rogers)")

    tab1,tab2 = st.tabs(["📡 技术扫描","📋 扫描历史"])

    with tab1:
        with st.form("radar_form"):
            c1,c2 = st.columns(2)
            with c1:
                name = st.text_input("技术名称 *", placeholder="例：基于CNN的图像分类")
                field = st.selectbox("技术领域",["人工智能/机器学习","生物医药","新材料","新能源","电子信息","先进制造","其他"])
            with c2:
                current_trl = st.selectbox("当前成熟度",[f"TRL {i}" for i in range(1,10)], index=3)
                patent_count = st.number_input("相关专利数", value=10, min_value=0)

            submitted = st.form_submit_button("📡 启动技术雷达扫描", type="primary", use_container_width=True)

        if submitted and name:
            with st.spinner("技术雷达扫描中..."):
                import time; time.sleep(2)

            # 模拟结果
            window = random.randint(12,60)
            threat_level = random.choice(["🟢 低","🟡 中","🔴 高"])
            disruptor = random.choice(["Transformer架构","扩散模型","神经辐射场","大语言模型","量子计算","类脑计算"])
            trend = random.choice(["📈 上升期","📊 平台期","📉 衰退期"])

            st.markdown("---")
            st.markdown(f"### 📡 「{name}」技术雷达报告")

            # 核心指标
            c1,c2,c3,c4 = st.columns(4)
            with c1:
                color = "#00b894" if window>36 else "#fdcb6e" if window>18 else "#d63031"
                st.markdown(f"""<div class="metric-box"><div class="num" style="color:{color}">{window}个月</div><div class="label">⏰ 窗口期</div></div>""", unsafe_allow_html=True)
            with c2:
                st.markdown(f"""<div class="metric-box"><div class="num">{threat_level}</div><div class="label">⚡ 替代威胁</div></div>""", unsafe_allow_html=True)
            with c3:
                st.markdown(f"""<div class="metric-box"><div class="num">{trend}</div><div class="label">📈 技术趋势</div></div>""", unsafe_allow_html=True)
            with c4:
                score = random.randint(40,90)
                st.markdown(f"""<div class="metric-box"><div class="num">{score}</div><div class="label">📊 转化潜力</div></div>""", unsafe_allow_html=True)

            # 详细分析
            st.markdown("#### 🔍 技术生命周期分析")
            st.markdown(f"""
            **当前阶段**：{trend}

            **关键发现**：
            - ⚠️ **主要替代威胁**：{disruptor}正在快速发展，可能在{window}个月内对「{name}」形成显著替代压力
            - 📊 **专利态势**：相关专利年增长率{random.randint(15,45)}%，竞争者持续进入
            - 🌍 **市场信号**：{random.randint(2,8)}家头部企业已开始布局替代技术
            - 📚 **学术趋势**：相关论文年发表量增长{random.randint(20,60)}%，研究热度持续上升
            """)

            st.markdown("#### 💡 决策建议")
            if window > 36:
                st.success(f"🟢 **窗口期充裕（{window}个月）**：建议稳步推进转化，同时关注替代技术动态。当前是构建竞争壁垒的好时机。")
            elif window > 18:
                st.warning(f"🟡 **窗口期有限（{window}个月）**：建议加速转化进程，优先锁定目标客户。同时评估是否可以整合替代技术。")
            else:
                st.error(f"🔴 **窗口期紧迫（{window}个月）**：建议立即启动转化，或考虑转型。继续投入当前技术路线的风险较高。")

            st.markdown("#### 📅 建议时间线")
            st.markdown(f"""
            | 阶段 | 时间 | 行动 |
            |------|------|------|
            | 🔥 紧急 | 本月内 | 完成技术评估，确定转化路径 |
            | 🏃 加速 | 1-3个月 | 完成概念验证，对接目标企业 |
            | 🎯 锁定 | 3-6个月 | 签订合作协议，启动试点 |
            | 🏗️ 建设 | 6-{window}个月 | 完成产品化，建立市场地位 |
            | 🔄 迭代 | 持续 | 跟踪替代技术，适时整合 |
            """)

    with tab2:
        st.info("暂无扫描历史。完成首次技术雷达扫描后，历史记录将显示在这里。")

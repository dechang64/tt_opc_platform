"""首页 - 平台总览"""
import streamlit as st

def render():
    st.markdown("""<div class="main-header">
    <h1>🚀 TT-OPC 智能运营平台</h1>
    <p>用AI赋能技术转移，让一个人成为一支团队 · 基于24个经济学理论设计</p>
    <div style="margin-top:.5rem">
        <span class="theory-tag">Arrow信息悖论</span>
        <span class="theory-tag">Coase交易成本</span>
        <span class="theory-tag">内生增长</span>
        <span class="theory-tag">三螺旋</span>
        <span class="theory-tag">联邦学习</span>
        <span class="theory-tag">创造性破坏</span>
        <span class="theory-tag">吸收能力</span>
    </div>
</div>""", unsafe_allow_html=True)

    # 全链路流程
    st.markdown("### 🔄 技术转移全链路")
    st.markdown("""<div class="pipeline">
        <span class="step">🔍 发现</span><span class="arrow">→</span>
        <span class="step">📦 盲盒评估</span><span class="arrow">→</span>
        <span class="step">🔗 联邦匹配</span><span class="arrow">→</span>
        <span class="step">🔄 场景翻译</span><span class="arrow">→</span>
        <span class="step">📡 技术雷达</span><span class="arrow">→</span>
        <span class="step">🌐 社交传播</span><span class="arrow">→</span>
        <span class="step">💰 交易成交</span>
    </div>""", unsafe_allow_html=True)

    # 8大使能功能
    st.markdown("### 🧩 八大使能功能")
    st.caption("不是让已有的流程更高效（优化器），而是让以前不可能的事成为可能（使能器）")

    features = [
        ("📦", "盲盒评估 TechBlindBox", "不泄露技术就能评估价值",
         "买方看到AI评估摘要而非技术细节，打破Arrow信息悖论",
         "Arrow信息悖论 + RAG", "✅ 可用"),
        ("🔗", "联邦匹配 FedMatch", "跨校专利数据不出校就能匹配",
         "联邦学习广播需求，各校本地匹配，只返回结果",
         "联邦学习经济学 + FL", "🔧 试点中"),
        ("🌐", "知识图谱 KnowledgeFlow", "看到知识从论文到产品的完整路径",
         "多源数据关联，量化知识流动效率",
         "内生增长理论 + KG", "📋 设计中"),
        ("📡", "技术雷达 TechRadar", "预测技术还有多久被替代",
         "多维数据驱动的技术生命周期预测",
         "创造性破坏 + 预测模型", "📋 设计中"),
        ("🔄", "场景翻译 TechTranslator", "同一技术给不同人看不同版本",
         "一键生成院长版/CEO版/投资人版",
         "吸收能力理论 + LLM", "✅ 可用"),
        ("🧬", "三角色工作台 TripleHelix", "一个人同时是教授+CEO+律师",
         "多智能体协同，共享项目上下文",
         "三螺旋理论 + Multi-Agent", "✅ 可用"),
        ("🌐", "社交传播交易 SocialHub", "一个人同时搞定社交+传播+交易",
         "AI辅助内容生成+智能撮合+全流程交易管理",
         "网络效应 + 双边市场 + 声誉机制", "✅ 可用"),
        ("🌡️", "创新温度计 InnovationThermo", "实时测量AI在技术转移中的渗透率",
         "平台数据反哺政策制定",
         "GPT渗透 + 任务模型", "📋 设计中"),
    ]

    cols = st.columns(4)
    for i, (icon, name, impossible, possible, theory, status) in enumerate(features):
        with cols[i % 4]:
            st.markdown(f"""<div class="card">
                <div style="font-size:2rem">{icon}</div>
                <h3>{name}</h3>
                <p><strong>以前不可能</strong>：{impossible}</p>
                <p><strong>现在可能</strong>：{possible}</p>
                <p style="font-size:.7rem;color:#636e72">📐 {theory}</p>
                <p>{status}</p>
            </div>""", unsafe_allow_html=True)

    # 统计
    st.markdown("### 📈 平台数据")
    c1,c2,c3,c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="metric-box"><div class="num">{len(st.session_state.get('assessments',[]))}</div><div class="label">盲盒评估</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-box"><div class="num">{len(st.session_state.get('matches',[]))}</div><div class="label">联邦匹配</div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-box"><div class="num">{len(st.session_state.get('bps',[]))}</div><div class="label">场景翻译</div></div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-box"><div class="num">{len(st.session_state.get('contracts',[]))}</div><div class="label">合同生成</div></div>""", unsafe_allow_html=True)

    # 与竞品对比
    st.markdown("### ⚔️ 与现有产品的本质区别")
    st.markdown("""<div class="card">
    <table style="width:100%;font-size:.85rem;border-collapse:collapse">
    <tr style="background:#f0f4ff"><th style="padding:.5rem;text-align:left">维度</th><th>科易网/智慧芽</th><th>Wellspring</th><th style="background:#e8f5e9">TT-OPC</th></tr>
    <tr><td style="padding:.5rem;border-bottom:1px solid #eee">定位</td><td>信息展示</td><td>流程管理</td><td style="background:#e8f5e9;font-weight:700">使能创造</td></tr>
    <tr><td style="padding:.5rem;border-bottom:1px solid #eee">AI能力</td><td>关键词匹配</td><td>规则引擎</td><td style="background:#e8f5e9;font-weight:700">LLM+联邦学习+多智能体</td></tr>
    <tr><td style="padding:.5rem;border-bottom:1px solid #eee">跨校匹配</td><td>❌</td><td>❌</td><td style="background:#e8f5e9;font-weight:700">✅ 联邦学习</td></tr>
    <tr><td style="padding:.5rem;border-bottom:1px solid #eee">信息保护</td><td>需NDA</td><td>需NDA</td><td style="background:#e8f5e9;font-weight:700">✅ 盲盒评估</td></tr>
    <tr><td style="padding:.5rem;border-bottom:1px solid #eee">场景翻译</td><td>❌</td><td>❌</td><td style="background:#e8f5e9;font-weight:700">✅ 多版本生成</td></tr>
    <tr><td style="padding:.5rem">目标用户</td><td>TTO机构</td><td>大企业</td><td style="background:#e8f5e9;font-weight:700">OPC个人</td></tr>
    </table></div>""", unsafe_allow_html=True)

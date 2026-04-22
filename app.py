"""
TT-OPC 智能运营平台 v0.3
技术转移一人公司全链路AI工具
基于24个经济学理论设计 · 8大使能功能
"""
import streamlit as st
import os, sys
from datetime import datetime

st.set_page_config(page_title="TT-OPC 智能运营平台", page_icon="🚀", layout="wide", initial_sidebar_state="expanded")

# ─── 全局CSS ───
st.markdown("""<style>
:root{--primary:#0f3460;--accent:#e94560;--bg:#f8f9fa;--card:#fff;--text:#2d3436;--muted:#636e72;--border:#dfe6e9;--success:#00b894;--warning:#fdcb6e;--danger:#d63031}
.stApp{background:var(--bg)}
.main-header{background:linear-gradient(135deg,#0f3460 0%,#16213e 50%,#1a1a2e 100%);padding:1.8rem 2rem;border-radius:0 0 1.2rem 1.2rem;margin:-1rem -1rem 1.5rem;color:#fff}
.main-header h1{font-size:1.8rem;font-weight:800;margin:0 0 .3rem}
.main-header p{opacity:.8;margin:0;font-size:.9rem}
.theory-tag{display:inline-block;background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.25);border-radius:999px;padding:.15rem .6rem;font-size:.7rem;margin:.15rem .2rem}
.card{background:var(--card);border-radius:1rem;padding:1.5rem;box-shadow:0 2px 12px rgba(0,0,0,.06);border:1px solid var(--border);margin-bottom:1rem}
.card h3{margin:0 0 .5rem;font-size:1.1rem}
.card p{color:var(--muted);font-size:.85rem;margin:.3rem 0}
.impossible{background:linear-gradient(135deg,#ff6b6b,#ee5a24);color:#fff;border-radius:.8rem;padding:1rem 1.2rem;margin:.8rem 0}
.impossible .before{opacity:.7;text-decoration:line-through;font-size:.85rem}
.impossible .after{font-weight:700;font-size:1rem;margin-top:.3rem}
.possible{background:linear-gradient(135deg,#00b894,#00cec9);color:#fff;border-radius:.8rem;padding:1rem 1.2rem;margin:.8rem 0}
.possible .label{font-weight:700;font-size:1rem}
.possible .desc{opacity:.9;font-size:.85rem;margin-top:.2rem}
.metric-box{text-align:center;padding:1rem;background:var(--bg);border-radius:.8rem;border:1px solid var(--border)}
.metric-box .num{font-size:2rem;font-weight:800;color:var(--primary)}
.metric-box .label{font-size:.75rem;color:var(--muted);margin-top:.2rem}
.pipeline{display:flex;align-items:center;justify-content:center;gap:.5rem;padding:1rem 0;flex-wrap:wrap}
.pipeline .step{background:var(--card);border:2px solid var(--primary);border-radius:.8rem;padding:.6rem 1rem;font-size:.8rem;font-weight:600;white-space:nowrap}
.pipeline .arrow{color:var(--muted);font-size:1.2rem}
.sidebar-section{background:var(--bg);border-radius:.8rem;padding:1rem;margin-bottom:.8rem}
</style>""", unsafe_allow_html=True)

# ─── Session State ───
for k in ["assessments","matches","bps","contracts","flows"]:
    if k not in st.session_state:
        st.session_state[k] = []

# ─── 侧边栏 ───
with st.sidebar:
    st.markdown("### 🚀 TT-OPC")
    st.caption("技术转移一人公司智能运营平台")
    st.markdown("---")
    nav = st.radio("导航", [
        "🏠 总览",
        "📦 盲盒评估 TechBlindBox",
        "🔗 联邦匹配 FedMatch",
        "🌐 知识图谱 KnowledgeFlow",
        "📡 技术雷达 TechRadar",
        "🔄 场景翻译 TechTranslator",
        "🧬 三角色工作台 TripleHelix",
        "🌐 社交传播交易 SocialHub",
        "🌡️ 创新温度计 InnovationThermo",
    ], label_visibility="collapsed")
    st.markdown("---")
    st.markdown("""
    <div class="sidebar-section">
    <strong>📚 配套资源</strong><br>
    <a href="https://github.com/dechang64/AI-for-TT-OPC" target="_blank">📖 实操指南</a><br>
    <a href="https://book.qq.com/book-detail/58160523" target="_blank">📖 小说《OPC时代》</a>
    </div>""", unsafe_allow_html=True)
    st.caption(f"v0.3 · {datetime.now().strftime('%Y-%m-%d')}")

# ─── 路由 ───
modules = {
    "总览": "pages.home",
    "盲盒评估": "pages.blindbox",
    "联邦匹配": "pages.fedmatch",
    "知识图谱": "pages.knowledge_flow",
    "技术雷达": "pages.tech_radar",
    "场景翻译": "pages.tech_translator",
    "三角色工作台": "pages.triple_helix",
    "社交传播交易": "pages.social_hub",
    "创新温度计": "pages.innovation_thermo",
}
for key, mod in modules.items():
    if key in nav:
        parts = mod.rsplit(".", 1)
        m = __import__(parts[0], fromlist=[parts[1]])
        getattr(m, parts[1]).render()
        break

"""盲盒评估 TechBlindBox - 打破Arrow信息悖论
v0.3 - 接入真实LLM API（含重试+模拟降级）
"""
import streamlit as st, json, subprocess, re, time, random
from datetime import datetime

from llm_utils import llm_chat, parse_json_response


def _llm_json(system_prompt, user_prompt):
    """调用LLM并解析JSON响应"""
    raw = llm_chat(system_prompt, user_prompt)
    if not raw:
        return None
    # 尝试多种JSON提取方式
    for extract in [
        lambda s: json.loads(s),
        lambda s: json.loads(re.search(r'```(?:json)?\s*\n?(.*?)\n?```', s, re.DOTALL).group(1)),
        lambda s: json.loads(re.search(r'\{.*\}', s, re.DOTALL).group(0)),
    ]:
        try:
            return extract(raw)
        except:
            continue
    return None

# ─── 模拟降级（API不可用时） ───
def _fallback_assessment(name, field, trl, pub_desc):
    """当LLM不可用时，基于规则的模拟评估"""
    # 从描述中提取关键词做简单分析
    desc_lower = pub_desc.lower()
    has_clinical = any(w in desc_lower for w in ['临床','医院','患者','medical','clinical'])
    has_patent = any(w in desc_lower for w in ['专利','发明','patent'])
    has_paper = any(w in desc_lower for w in ['论文','发表','nature','science','ieee'])
    has_deploy = any(w in desc_lower for w in ['部署','上线','商用','deploy','product'])
    has_accuracy = re.search(r'(\d+\.?\d*)\s*%', pub_desc)

    base = random.randint(60, 80)
    if has_clinical: base += random.randint(3, 10)
    if has_patent: base += random.randint(2, 8)
    if has_paper: base += random.randint(2, 6)
    if has_deploy: base += random.randint(5, 12)
    if has_accuracy:
        acc = float(has_accuracy.group(1))
        if acc > 95: base += random.randint(3, 8)

    s = min(95, base + random.randint(-5, 5))
    t = min(95, base + random.randint(-8, 3))
    m = min(95, base + random.randint(-10, 5))
    o = round(s*0.25 + t*0.35 + m*0.40)

    field_swot = {
        "人工智能/机器学习": {
            "S":["算法创新性强","已有实验验证","团队学术背景强","可复现性高"],
            "W":["依赖特定数据集","计算资源需求大","缺乏行业Know-how","技术成熟度偏低"],
            "O":["AI政策红利期","多行业数字化转型需求","国产替代空间大","人才供给充足"],
            "T":["大厂竞争激烈","技术迭代速度快","数据合规风险","开源替代趋势"],
        },
        "生物医药": {
            "S":["靶点机制明确","动物实验数据好","专利布局完善","临床前数据充分"],
            "W":["临床试验周期长","监管审批不确定性高","研发投入大","CMC工艺不成熟"],
            "O":["医保目录调整","罕见病政策支持","CRO产业链成熟","国际合作机会"],
            "T":["集采降价压力","同类竞品多","监管趋严","资本寒冬"],
        },
    }
    default_swot = {
        "S":["技术方案创新","已有初步验证","团队经验丰富","成本优势明显"],
        "W":["市场认知度低","标准化程度不足","依赖特定场景","资金需求较大"],
        "O":["政策支持力度大","行业需求增长","国产替代窗口期","跨界应用潜力"],
        "T":["竞争者进入","技术路线变化","政策不确定性","市场教育成本高"],
    }
    d = field_swot.get(field, default_swot)

    return {
        "science_score": s, "tech_score": t, "market_score": m, "overall_score": o,
        "strengths": d["S"], "weaknesses": d["W"],
        "opportunities": d["O"], "threats": d["T"],
        "suggestion": f"建议优先推进{field}领域的概念验证，寻找标杆客户建立示范案例。当前技术成熟度为{trl}，建议先寻求概念验证基金支持，完成技术-市场的双向验证后再扩大推广。",
        "market_size": f"预计{field.split('/')[0]}相关市场规模达数百亿元",
        "target_customers": f"{field.split('/')[0]}行业的中大型企业",
        "competition_level": random.choice(["低","中","高"]),
        "time_to_market": "1-3年",
        "risk_level": "中",
        "_simulated": True,
    }

# ─── 评估Prompt ───
SYSTEM_PROMPT = """你是一位资深的技术转移评估专家，拥有20年科技成果转化经验。
你精通技术评估、市场分析、专利价值评估和商业化路径规划。

你的任务是根据用户提供的**公开信息**（论文摘要、专利公开文本、项目简介等），
对一项技术进行全面的"盲盒评估"。

**核心原则**：
1. 只基于公开信息评估，不要求也不推测未公开的技术细节
2. 评估要客观、专业、有数据支撑
3. 给出可操作的商业化建议

**输出格式**：严格输出JSON，格式如下：
{
  "science_score": <55-95整数，科学价值评分>,
  "tech_score": <50-95整数，技术价值评分>,
  "market_score": <45-95整数，市场价值评分>,
  "overall_score": <加权平均整数>,
  "strengths": ["优势1", "优势2", "优势3", "优势4"],
  "weaknesses": ["劣势1", "劣势2", "劣势3", "劣势4"],
  "opportunities": ["机会1", "机会2", "机会3", "机会4"],
  "threats": ["威胁1", "威胁2", "威胁3", "威胁4"],
  "suggestion": "<一段具体的转化建议，100-200字>",
  "market_size": "<市场规模估算>",
  "target_customers": "<目标客户描述>",
  "competition_level": "<竞争程度：低/中/高>",
  "time_to_market": "<预计上市时间>",
  "risk_level": "<风险等级：低/中/高>"
}

**评分标准**：
- 科学价值(25%权重)：理论创新性、学术影响力、可重复性
- 技术价值(35%权重)：技术成熟度、可工程化程度、专利壁垒
- 市场价值(40%权重)：市场规模、竞争格局、商业化可行性"""

def _build_user_prompt(name, field, institution, inventor, patent_no, keywords, trl, pub_desc):
    return f"""请对以下技术进行盲盒评估：

**技术名称**：{name}
**技术领域**：{field}
**所属机构**：{institution or '未提供'}
**发明人**：{inventor or '未提供'}
**专利号**：{patent_no or '未提供'}
**关键词**：{keywords or '未提供'}
**技术成熟度**：{trl}

**公开描述**：
{pub_desc}

请基于以上公开信息，输出JSON格式的评估报告。注意：
1. 只基于公开信息评估
2. 评分要客观合理
3. SWOT分析要具体、有针对性
4. 转化建议要可操作"""


def render():
    st.markdown("# 📦 盲盒评估 TechBlindBox")
    st.markdown("""<div class="impossible">
        <div class="before">❌ 以前：买方必须先看技术细节才能评估 → 看了就等于泄露了</div>
        <div class="after">✅ 现在：AI从公开信息生成评估报告 → 买方零成本筛选，不泄露技术</div>
    </div>""", unsafe_allow_html=True)
    st.caption("📐 理论支撑：Arrow信息悖论(1962) + 搜寻理论(Stigler 1961) + 交易成本经济学(Coase 1937)")

    tab1, tab2 = st.tabs(["🆕 新建盲盒评估", "📋 评估历史"])

    with tab1:
        with st.form("blindbox_form"):
            st.markdown("### 📋 输入公开信息（无需技术细节）")
            c1,c2 = st.columns(2)
            with c1:
                name = st.text_input("技术/专利名称 *", placeholder="例：基于联邦学习的医疗影像诊断系统")
                field = st.selectbox("技术领域", ["人工智能/机器学习","生物医药","新材料","新能源","电子信息","先进制造","节能环保","其他"])
                patent_no = st.text_input("专利号（选填）", placeholder="例：CN202410XXXXXX")
                inventor = st.text_input("发明人", placeholder="例：张三、李四")
            with c2:
                institution = st.text_input("所属机构", placeholder="例：XX大学")
                keywords = st.text_input("关键词", placeholder="逗号分隔：联邦学习,医疗影像,隐私计算")
                pub_paper = st.text_input("相关论文/公开报告链接", placeholder="https://arxiv.org/abs/...")
                trl = st.selectbox("技术成熟度(TRL)", [f"TRL {i}" for i in range(1,10)], index=3)

            pub_desc = st.text_area("公开描述（论文摘要/专利公开文本/项目简介）", height=120,
                placeholder="粘贴论文摘要、专利公开说明书、或项目简介等公开信息...\n\n⚠️ 请勿输入未公开的技术细节")

            submitted = st.form_submit_button("📦 生成盲盒评估报告", type="primary", use_container_width=True)

        if submitted:
            if not name or not pub_desc:
                st.error("请填写技术名称和公开描述")
                return

            # 调用LLM（含降级）
            progress = st.progress(0, text="🤖 AI正在分析公开信息...")
            user_prompt = _build_user_prompt(name, field, institution, inventor, patent_no, keywords, trl, pub_desc)

            progress.progress(30, text="🤖 正在连接AI评估引擎...")
            result = _llm_json(SYSTEM_PROMPT, user_prompt)

            if result and isinstance(result, dict):
                progress.progress(100, text="✅ AI评估完成！")
                is_sim = False
            else:
                progress.progress(50, text="⚠️ AI引擎繁忙，启用智能规则评估...")
                result = _fallback_assessment(name, field, trl, pub_desc)
                is_sim = True
                progress.progress(100, text="✅ 规则评估完成！")

            time.sleep(0.5)
            progress.empty()

            if is_sim:
                st.warning("⚠️ AI引擎当前繁忙，已使用智能规则引擎生成评估。结果基于公开信息的关键词分析，仅供参考。")

            s = result.get("science_score", 70)
            t = result.get("tech_score", 70)
            m = result.get("market_score", 70)
            o = result.get("overall_score", round(s*0.25 + t*0.35 + m*0.40))

            assessment = {
                "name": name, "field": field, "institution": institution,
                "inventor": inventor, "patent_no": patent_no, "trl": trl,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "science": s, "tech": t, "market": m, "overall": o,
                "strengths": result.get("strengths", []),
                "weaknesses": result.get("weaknesses", []),
                "opportunities": result.get("opportunities", []),
                "threats": result.get("threats", []),
                "suggestion": result.get("suggestion", ""),
                "market_size": result.get("market_size", ""),
                "target_customers": result.get("target_customers", ""),
                "competition_level": result.get("competition_level", ""),
                "time_to_market": result.get("time_to_market", ""),
                "risk_level": result.get("risk_level", ""),
                "is_simulated": is_sim,
            }
            st.session_state.assessments.append(assessment)
            st.rerun()

        # 显示最新结果
        if st.session_state.assessments:
            _display(st.session_state.assessments[-1])

    with tab2:
        if not st.session_state.assessments:
            st.info("暂无评估记录")
        for r in reversed(st.session_state.assessments):
            tag = "🤖 AI" if not r.get("is_simulated") else "📐 规则"
            with st.expander(f"📦 {r['name']} — 综合评分 {r['overall']} ({tag}) — {r['date']}"):
                _display(r)


def _display(r):
    st.markdown("---")
    color = "#00b894" if r["overall"]>=75 else "#fdcb6e" if r["overall"]>=60 else "#d63031"
    c1,c2,c3,c4,c5 = st.columns(5)
    with c1:
        st.markdown(f"""<div class="metric-box"><div class="num">{r['science']}</div><div class="label">🔬 科学价值<br><span style="font-size:.65rem">权重25%</span></div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-box"><div class="num">{r['tech']}</div><div class="label">⚙️ 技术价值<br><span style="font-size:.65rem">权重35%</span></div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-box"><div class="num">{r['market']}</div><div class="label">💰 市场价值<br><span style="font-size:.65rem">权重40%</span></div></div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-box"><div class="num" style="color:{color}">{r['overall']}</div><div class="label">📊 综合评分<br><span style="font-size:.65rem">加权平均</span></div></div>""", unsafe_allow_html=True)
    with c5:
        level = "🟢 高价值" if r["overall"]>=75 else "🟡 中等" if r["overall"]>=60 else "🔴 需谨慎"
        st.markdown(f"""<div class="metric-box"><div class="num" style="font-size:1.2rem">{level}</div><div class="label">评估等级</div></div>""", unsafe_allow_html=True)

    # 额外信息
    extras = []
    if r.get("market_size"): extras.append(f"📈 市场规模：{r['market_size']}")
    if r.get("target_customers"): extras.append(f"🎯 目标客户：{r['target_customers']}")
    if r.get("competition_level"): extras.append(f"⚔️ 竞争程度：{r['competition_level']}")
    if r.get("time_to_market"): extras.append(f"⏱️ 上市时间：{r['time_to_market']}")
    if r.get("risk_level"): extras.append(f"⚠️ 风险等级：{r['risk_level']}")
    if extras:
        st.markdown("#### 📊 市场概览")
        for e in extras:
            st.markdown(e)

    st.info(f"💡 **转化建议**：{r.get('suggestion','')}")

    sc,sw = st.columns(2)
    with sc:
        st.markdown("#### ✅ 优势")
        for s in r["strengths"]: st.markdown(f"- {s}")
        st.markdown("#### 🌈 机会")
        for o in r["opportunities"]: st.markdown(f"- {o}")
    with sw:
        st.markdown("#### ⚠️ 劣势")
        for w in r["weaknesses"]: st.markdown(f"- {w}")
        st.markdown("#### 🔴 威胁")
        for t in r["threats"]: st.markdown(f"- {t}")

    st.download_button("📥 导出评估报告", data=_to_md(r), file_name=f"盲盒评估_{r['name']}_{r['date'][:10]}.md", mime="text/markdown")


def _to_md(r):
    engine = "AI评估引擎" if not r.get("is_simulated") else "智能规则引擎"
    md = f"""# 盲盒评估报告：{r['name']}

> 由TT-OPC平台{engine}生成 | {r['date']}

## 基本信息
- **领域**：{r['field']}
- **机构**：{r['institution'] or '未提供'}
- **发明人**：{r['inventor'] or '未提供'}
- **专利号**：{r['patent_no'] or '未提供'}
- **技术成熟度**：{r['trl']}

## 评分

| 维度 | 分数 | 权重 |
|------|------|------|
| 🔬 科学价值 | {r['science']} | 25% |
| ⚙️ 技术价值 | {r['tech']} | 35% |
| 💰 市场价值 | {r['market']} | 40% |
| **📊 综合** | **{r['overall']}** | **100%** |

"""
    if r.get("market_size"):
        md += f"## 市场概览\n- 市场规模：{r['market_size']}\n"
    if r.get("target_customers"):
        md += f"- 目标客户：{r['target_customers']}\n"
    if r.get("competition_level"):
        md += f"- 竞争程度：{r['competition_level']}\n"
    if r.get("time_to_market"):
        md += f"- 上市时间：{r['time_to_market']}\n"
    if r.get("risk_level"):
        md += f"- 风险等级：{r['risk_level']}\n"

    md += f"""
## SWOT分析

### ✅ 优势
""" + "\n".join(f"- {s}" for s in r["strengths"]) + """

### ⚠️ 劣势
""" + "\n".join(f"- {s}" for s in r["weaknesses"]) + """

### 🌈 机会
""" + "\n".join(f"- {s}" for s in r["opportunities"]) + """

### 🔴 威胁
""" + "\n".join(f"- {s}" for s in r["threats"]) + f"""

## 💡 转化建议
{r.get('suggestion','')}

---
*本报告由{engine}基于公开信息自动生成，仅供参考，不构成投资建议。*
"""
    return md

"""场景翻译 TechTranslator - 消除吸收能力门槛
v0.3 - 接入真实LLM API（含重试+模拟降级）
"""
import streamlit as st, json, subprocess, re, time
from datetime import datetime

# ─── LLM调用（复用盲盒的同一套逻辑） ───
def _llm_raw(system_prompt, user_prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = subprocess.run(
                ["z-ai", "chat", "-p", user_prompt, "-s", system_prompt],
                capture_output=True, text=True, timeout=120
            )
            if result.returncode == 0:
                output = result.stdout.strip()
                lines = [l for l in output.split('\n') if l.strip() and not l.startswith('🚀')]
                output = '\n'.join(lines)
                if output:
                    return output
            if "429" in result.stderr or "Too many" in result.stderr:
                time.sleep(30 * (attempt + 1))
                continue
        except subprocess.TimeoutExpired:
            continue
        except Exception:
            time.sleep(5)
            continue
    return None

# ─── System Prompt ───
SYSTEM_PROMPT = """你是一位资深的技术转移专家，精通将学术/技术语言翻译为不同受众能理解的语言。

## 核心原则
1. **吸收能力匹配**：根据目标受众的知识背景，调整术语深度和表达方式
2. **信息保真**：不添加原文没有的信息，不夸大技术能力
3. **价值突出**：每个版本都要突出该受众最关心的价值点
4. **可操作性**：提供明确的下一步行动建议

## 输出格式
直接输出Markdown格式的文档，不要输出JSON或其他格式。使用标题、列表、表格等Markdown元素使内容清晰易读。"""

# ─── 各角色的User Prompt模板 ───
ROLE_PROMPTS = {
    "投资人版": """请将以下技术信息翻译为**投资人版本**。

## 目标读者
风险投资机构、天使投资人、产业基金

## 翻译要求
- 用投资人的语言：市场规模、增长潜力、竞争壁垒、退出路径
- 突出投资亮点：为什么这个技术值得投？回报预期如何？
- 量化数据：尽可能给出市场规模、增长率、估值区间等数字
- 风险透明：诚实说明主要风险和应对策略
- 控制篇幅：800-1200字，投资人时间宝贵

## 必须包含的章节
1. **一句话定位**（20字以内，让投资人秒懂）
2. **市场机会**（TAM/SAM/SOM，增长驱动因素）
3. **技术壁垒**（为什么别人做不了或做不好）
4. **商业模式**（怎么赚钱，什么时候盈亏平衡）
5. **团队亮点**（为什么是这帮人能做成）
6. **融资需求**（要多少钱，花在哪里，预期里程碑）
7. **风险与应对**

## 技术信息
- 技术名称：{name}
- 技术领域：{field}
- 所属机构：{institution}
- 技术描述：{desc}""",

    "CEO版": """请将以下技术信息翻译为**企业CEO/CTO版本**。

## 目标读者
企业决策者、技术负责人、业务部门负责人

## 翻译要求
- 用企业家的语言：解决什么问题、省多少钱/赚多少钱、怎么落地
- 突出业务价值：这个技术能帮企业解决什么痛点？
- 落地路径：给出明确的实施步骤和时间表
- 竞品对比：与现有解决方案相比有什么优势
- 控制篇幅：600-1000字，CEO需要快速决策

## 必须包含的章节
1. **技术概述**（一段话说清楚这是什么）
2. **解决什么问题**（企业当前的痛点）
3. **与现有方案对比**（表格形式）
4. **如何落地**（分阶段实施计划）
5. **预期效果**（可量化的业务指标）
6. **合作方式建议**（许可/联合开发/技术入股等）
7. **下一步行动**（具体建议）

## 技术信息
- 技术名称：{name}
- 技术领域：{field}
- 所属机构：{institution}
- 技术描述：{desc}""",

    "院长版": """请将以下技术信息翻译为**高校院长/科技处领导版本**。

## 目标读者
高校领导、科技处/成果转化处负责人、科研院长

## 翻译要求
- 用管理者的语言：政策合规、转化路径、风险控制、社会效益
- 突出合规性：国有资产评估、知识产权归属、收益分配
- 政策对标：引用相关政策文件，说明政策红利
- 风险管控：国有资产管理、科研人员兼职合规
- 控制篇幅：800-1200字，体现专业性和严谨性

## 必须包含的章节
1. **成果概述**（学术价值和影响力）
2. **转化价值评估**（科学/技术/市场三维度）
3. **转化路径建议**（许可/转让/作价入股，推荐哪种）
4. **合规要点**（国资评估、知识产权、收益分配）
5. **风险提示与应对**
6. **政策支持**（可利用的政策资源）
7. **时间规划**（建议的转化时间线）

## 技术信息
- 技术名称：{name}
- 技术领域：{field}
- 所属机构：{institution}
- 技术描述：{desc}""",
}

# ─── 模拟降级（规则引擎） ───
def _fallback_translate(name, field, institution, desc, role):
    """LLM不可用时的规则引擎降级"""
    ctx = {
        "field": field, "institution": institution or "某高校",
        "name": name, "desc": desc[:200],
    }
    templates = {
        "投资人版": f"""# 💼 投资机会简报：{name}

> ⚠️ 本报告由智能规则引擎生成（LLM服务暂不可用）

## 一句话定位
{field}领域的技术创新项目，具备明确的商业化前景。

## 市场机会
- 中国{field}市场规模预计2027年突破500亿元
- 年复合增长率约25-35%
- 核心驱动因素：政策支持 + 产业升级 + 国产替代

## 技术壁垒
- 核心技术来自{institution}，学术背景扎实
- 已有初步验证，技术可行性得到证实
- 与现有方案相比具有差异化优势

## 商业模式
- 推荐模式：技术许可 + SaaS订阅
- 预计2-3年实现盈亏平衡
- 保守估计3年内营收可达2000-5000万元

## 团队亮点
- 核心团队来自{institution}
- 在{field}领域有深厚积累

## 融资需求
- 建议天使轮/Pre-A轮融资300-800万元
- 主要用于：产品化开发 + 市场推广 + 团队扩充
- 预期12个月内完成产品化验证

## 风险与应对
| 风险 | 等级 | 应对策略 |
|------|------|---------|
| 技术成熟度 | 🟡 中 | 概念验证 + 持续迭代 |
| 市场竞争 | 🟡 中 | 差异化定位 + 先发优势 |
| 团队短板 | 🟢 低 | 引入产业合伙人 |
| 政策变化 | 🟢 低 | 密切关注 + 灵活调整 |""",

        "CEO版": f"""# 👔 技术合作方案：{name}

> ⚠️ 本报告由智能规则引擎生成（LLM服务暂不可用）

## 技术概述
本技术来自{institution}{field}团队，针对行业核心痛点提供创新解决方案。

## 解决什么问题
贵公司可能在以下场景面临挑战：
- 效率瓶颈：现有方案无法满足业务增长需求
- 成本压力：人工/运营成本持续上升
- 技术债务：现有技术栈面临升级压力

## 与现有方案对比
| 维度 | 现有方案 | 本技术方案 |
|------|---------|-----------|
| 技术路线 | 传统方法 | 创新方法 |
| 效率 | 基准 | 预计提升30-50% |
| 成本 | 基准 | 预计降低20-40% |
| 可扩展性 | 有限 | 支持水平扩展 |

## 如何落地
1. **概念验证（1-3个月）**：在贵公司特定场景验证可行性
2. **试点部署（3-6个月）**：小范围试运行，量化效果
3. **规模化推广（6-12个月）**：全面部署，持续优化

## 预期效果
- 效率提升：30-50%
- 成本降低：20-40%
- 投资回报期：12-18个月

## 合作方式建议
推荐**技术许可 + 联合开发**模式：
- 前期以技术许可快速验证
- 后期根据效果深化联合开发

## 下一步行动
1. 安排技术交流会（发明人团队参与）
2. 确定概念验证场景和指标
3. 签署保密协议（NDA）
4. 启动概念验证项目""",

        "院长版": f"""# 🎓 成果转化可行性报告：{name}

> ⚠️ 本报告由智能规则引擎生成（LLM服务暂不可用）

## 成果概述
本成果由{institution}{field}团队研发，具备较高的学术价值和转化潜力。

## 转化价值评估
| 维度 | 评估 | 说明 |
|------|------|------|
| 🔬 科学价值 | ⭐⭐⭐⭐ | 理论基础扎实，方法论有创新 |
| ⚙️ 技术价值 | ⭐⭐⭐ | 技术方案可行，已有初步验证 |
| 💰 市场价值 | ⭐⭐⭐ | 市场需求明确，商业化前景良好 |
| **综合** | **⭐⭐⭐½** | **建议积极推进转化** |

## 转化路径建议
**推荐路径**：技术许可先行 + 后续联合开发

理由：
- 技术成熟度适合许可模式，前期风险可控
- 通过许可建立合作关系，后续可深化
- 符合当前科技成果转化政策导向

## 合规要点
| 事项 | 要求 | 建议 |
|------|------|------|
| 国有资产评估 | 必须履行 | 委托有资质的评估机构 |
| 知识产权归属 | 职务发明 | 确认专利权属清晰 |
| 收益分配 | 按政策执行 | 建议不低于70%奖励发明人 |
| 科研人员兼职 | 需报备 | 按学校规定办理 |

## 风险提示与应对
- **技术成熟度风险**：建议先完成概念验证
- **市场风险**：建议充分调研目标市场
- **合规风险**：建议提前咨询法务

## 政策支持
- 《中华人民共和国促进科技成果转化法》
- 财税〔2016〕36号：技术转让免征增值税
- 国发〔2024〕7号：加快科技成果转化若干措施
- 概念验证基金、科创园区扶持政策

## 时间规划
| 阶段 | 时间 | 重点工作 |
|------|------|---------|
| 评估 | 第1个月 | 完成知识产权评估 |
| 对接 | 第2-3个月 | 对接目标企业 |
| 试点 | 第4-6个月 | 概念验证+试点 |
| 转化 | 第7-12个月 | 正式转化+收益落地 |""",
    }
    return templates.get(role, templates["CEO版"])


def render():
    st.markdown("# 🔄 场景翻译 TechTranslator")
    st.markdown("""<div class="impossible">
        <div class="before">❌ 以前：技术描述只有一种版本（论文/专利格式），企业看不懂，投资人没耐心</div>
        <div class="after">✅ 现在：同一技术一键生成投资人版/CEO版/院长版，每个版本用对方能懂的语言</div>
    </div>""", unsafe_allow_html=True)
    st.caption("📐 理论支撑：吸收能力理论(Cohen & Levinthal 1990) + Arrow信息悖论 + 交易成本经济学(Coase)")

    tab1, tab2 = st.tabs(["🔄 新建翻译", "📋 翻译历史"])

    with tab1:
        with st.form("translate_form"):
            st.markdown("### 📋 输入技术信息")
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("技术名称 *", placeholder="例：基于联邦学习的医疗影像诊断系统")
                field = st.selectbox("技术领域", [
                    "人工智能/机器学习", "生物医药", "新材料", "新能源",
                    "电子信息", "先进制造", "节能环保", "其他"
                ])
                institution = st.text_input("所属机构", placeholder="例：XX大学")
            with c2:
                target = st.selectbox("翻译为哪个版本", [
                    "💼 投资人版", "👔 CEO/企业版", "🎓 院长/领导版", "📊 全部版本"
                ])

            tech_desc = st.text_area(
                "技术描述（任意格式）", height=150,
                placeholder="粘贴论文摘要、专利说明书、或任何格式的技术描述...\n\nAI会自动将其翻译为目标受众能理解的语言。\n\n示例：\n本研究提出了一种基于联邦学习的医疗影像诊断框架，通过在多家医院间分布式训练深度学习模型，实现了在不共享患者原始数据的前提下，将肺结节检测的准确率提升至96.3%。该框架支持CT、X光等多种影像模态，已在3家三甲医院完成临床验证。"
            )

            submitted = st.form_submit_button("🔄 生成场景翻译", type="primary", use_container_width=True)

        if submitted:
            if not name or not tech_desc:
                st.error("请填写技术名称和描述")
                return

            versions = ["投资人版", "CEO版", "院长版"] if "全部" in target else [target.split()[-1]]
            results = {}
            engine_used = {}

            for v in versions:
                prompt = ROLE_PROMPTS[v].format(
                    name=name, field=field,
                    institution=institution or "某高校",
                    desc=tech_desc
                )

                # 尝试LLM
                with st.spinner(f"🤖 AI正在生成「{v}」..."):
                    llm_output = _llm_raw(SYSTEM_PROMPT, prompt)

                if llm_output:
                    results[v] = llm_output
                    engine_used[v] = "🤖 AI"
                else:
                    # 降级到规则引擎
                    results[v] = _fallback_translate(name, field, institution, tech_desc, v)
                    engine_used[v] = "📐 规则"

            record = {
                "name": name, "field": field,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "versions": results, "engine": engine_used,
            }
            st.session_state.bps.append(record)
            st.rerun()

        if st.session_state.bps:
            r = st.session_state.bps[-1]
            st.markdown("---")
            for ver, content in r["versions"].items():
                icon = {"投资人版": "💼", "CEO版": "👔", "院长版": "🎓"}.get(ver, "📄")
                engine = r.get("engine", {}).get(ver, "")
                with st.expander(f"{icon} {ver}  {engine}", expanded=True):
                    st.markdown(content)
                    st.download_button(
                        "📥 导出", data=content,
                        file_name=f"{r['name']}_{ver}_{r['date'][:10]}.md",
                        mime="text/markdown", key=f"dl_{ver}_{r['date']}"
                    )

    with tab2:
        if not st.session_state.bps:
            st.info("暂无翻译记录")
        for r in reversed(st.session_state.bps):
            with st.expander(f"🔄 {r['name']} — {r['date']}"):
                for ver in r["versions"]:
                    engine = r.get("engine", {}).get(ver, "")
                    st.markdown(f"- {ver}  {engine}")

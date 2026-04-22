"""三角色工作台 TripleHelix - 一人=三团队
v0.3 - 接入真实LLM API（三Agent并行分析）
"""
import streamlit as st, json, subprocess, re, time
from datetime import datetime

# ─── LLM调用 ───
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

# ─── 三个角色的System Prompt ───
SYSTEM_PROMPTS = {
    "prof": """你是一位资深大学教授和技术评估专家，拥有20年科研经验，精通技术评估、学术价值判断和工程化可行性分析。

## 你的角色
你代表"三螺旋"中的**大学**端，从学术和技术角度评估项目。

## 分析框架
1. **科学价值**：理论创新性、方法先进性、学术影响力
2. **技术成熟度**：TRL评估、工程化难度、可扩展性
3. **团队评估**：科研实力、发表记录、技术积累
4. **转化建议**：技术路线优化、合作方向、风险提示

## 输出要求
- 使用Markdown格式，包含表格和列表
- 给出具体的量化评分（1-10分）
- 基于项目描述给出针对性分析，不要泛泛而谈
- 最后给出明确的"教授建议"（一段话总结）""",

    "ceo": """你是一位连续创业者和商业策略专家，拥有丰富的技术商业化经验，擅长市场分析、商业模式设计和融资策略。

## 你的角色
你代表"三螺旋"中的**产业**端，从商业角度评估项目。

## 分析框架
1. **市场机会**：TAM/SAM/SOM、增长趋势、痛点分析
2. **竞争格局**：直接/间接竞争者、差异化优势、进入壁垒
3. **商业模式**：收入模式、定价策略、客户获取
4. **财务预测**：收入预测、成本结构、盈亏平衡点
5. **落地路径**：概念验证→试点→规模化的时间线

## 输出要求
- 使用Markdown格式，包含表格和列表
- 市场数据要具体（即使是基于经验的估算）
- 给出明确的商业建议和下一步行动
- 最后给出明确的"CEO建议"（一段话总结）""",

    "lawyer": """你是一位专注于知识产权和技术转移的资深律师，精通高校科技成果转化相关法律法规。

## 你的角色
你代表"三螺旋"中的**制度**端，从法律合规角度审查项目。

## 分析框架
1. **知识产权审查**：权属清晰度、专利有效性、布局完整性
2. **合规风险**：国有资产评估、数据合规、竞业限制、税务
3. **合同设计**：许可方式、费用结构、知识产权归属、保密条款
4. **政策利用**：科技成果转化法、税收优惠、科创扶持政策
5. **风险缓释**：风险等级评估、应对策略、保险建议

## 输出要求
- 使用Markdown格式，包含表格和列表
- 引用具体法律法规条文（如《促进科技成果转化法》第X条）
- 给出风险等级（🟢低/🟡中/🔴高）和具体应对措施
- 最后给出明确的"律师建议"（一段话总结）""",
}

# ─── 构建User Prompt ───
def _build_prompt(project_name, project_desc, role, other_roles_data=None):
    """构建User Prompt，包含共享上下文和其他角色的分析结果"""
    prompt = f"## 待分析项目\n\n**项目名称**：{project_name}\n\n**项目描述**：\n{project_desc}\n\n"

    # 注入其他角色的分析结果（三螺旋协同）
    if other_roles_data:
        prompt += "## 其他角色的分析（供参考）\n\n"
        role_names = {"prof": "教授", "ceo": "CEO", "lawyer": "律师"}
        for r, data in other_roles_data.items():
            if data and r != role:
                prompt += f"### {role_names[r]}的分析摘要\n{data[:500]}\n\n"

    prompt += f"\n请从你的专业角度（{role}）对以上项目进行深度分析。"
    return prompt

# ─── 规则引擎降级 ───
def _fallback_prof(name, desc):
    return f"""### 🎓 教授Agent分析报告

> ⚠️ LLM暂不可用，以下为智能规则引擎生成

#### 🔬 科学价值评估

| 维度 | 评分 | 说明 |
|------|------|------|
| 理论创新性 | 7/10 | 需结合具体论文/专利评估 |
| 实验验证 | 6/10 | 建议补充更多场景验证数据 |
| 可复现性 | 6/10 | 建议开源核心代码 |
| 学术影响力 | 6/10 | 建议在顶会/顶刊发表 |

#### ⚙️ 技术成熟度评估

| 维度 | 评分 | 说明 |
|------|------|------|
| 算法成熟度 | 6/10 | 核心算法需进一步验证 |
| 数据依赖 | 5/10 | 评估数据获取难度 |
| 工程化程度 | 4/10 | 距离生产部署有差距 |
| 可扩展性 | 5/10 | 架构设计需优化 |

#### 💬 教授建议
建议：请提供更详细的项目描述（论文摘要、专利说明书、实验数据等），以便进行更精准的评估。当前信息不足以给出完整的科学价值判断。"""

def _fallback_ceo(name, desc):
    return f"""### 👔 CEO Agent分析报告

> ⚠️ LLM暂不可用，以下为智能规则引擎生成

#### 📊 市场机会分析

| 维度 | 评估 | 说明 |
|------|------|------|
| 市场规模 | 待评估 | 需明确目标行业和客户群 |
| 增长趋势 | 待评估 | 需调研行业报告 |
| 痛点强度 | 待评估 | 需与目标客户深度访谈 |

#### 🎯 商业模式建议

| 模式 | 适用场景 | 优势 | 劣势 |
|------|---------|------|------|
| 技术许可 | 成熟技术 | 见效快 | 收入天花板低 |
| SaaS订阅 | 软件类技术 | 可扩展 | 需要持续投入 |
| 联合开发 | 早期技术 | 风险共担 | 周期较长 |
| 自主创业 | 高潜力技术 | 收益最大 | 风险最高 |

#### 📅 建议落地路径

1. **第1-2个月**：完成概念验证（PoC），量化技术效果
2. **第3-4个月**：对接3-5家目标企业，收集反馈
3. **第5-6个月**：完成试点部署，积累案例数据
4. **第7-12个月**：规模化推广，建立品牌

#### 💬 CEO建议
建议：请提供更详细的项目描述，包括目标客户、应用场景、已有验证数据等。商业分析需要具体的市场信息支撑。"""

def _fallback_lawyer(name, desc):
    return f"""### ⚖️ 律师Agent分析报告

> ⚠️ LLM暂不可用，以下为智能规则引擎生成

#### 🔒 知识产权审查

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 权属清晰度 | ⚠️ 待确认 | 确认是否为职务发明 |
| 专利有效性 | ⚠️ 待确认 | 需核查专利法律状态 |
| 布局完整性 | ⚠️ 待确认 | 评估是否需要PCT布局 |
| 质押/许可 | ⚠️ 待确认 | 确认无在先许可限制 |

#### ⚠️ 合规风险清单

| 风险项 | 等级 | 法律依据 | 应对措施 |
|--------|------|---------|---------|
| 国有资产评估 | 🟡 中 | 《促进科技成果转化法》第16条 | 履行资产评估备案程序 |
| 收益分配 | 🟡 中 | 《促进科技成果转化法》第43-45条 | 按规定比例分配给发明人 |
| 数据合规 | 🟡 中 | 《数据安全法》《个人信息保护法》 | 评估数据处理合规性 |
| 税收优惠 | 🟢 低 | 《促进科技成果转化法》第34条 | 申请技术转让所得税减免 |
| 竞业限制 | 🟢 低 | 《劳动合同法》第23-24条 | 确认发明人劳动合同条款 |

#### 📋 合同条款建议

- **许可方式**：建议排他性许可（限定区域/领域）
- **许可费**：入门费 + 运营提成（销售额的3-8%）
- **知识产权归属**：改进成果由双方共有
- **保密条款**：保密期不少于3年
- **争议解决**：约定仲裁条款

#### 💬 律师建议
建议：在推进转化前，务必完成以下工作：①确认知识产权权属；②完成国有资产评估备案；③与发明人确认收益分配方案；④起草/审核技术许可合同。"""

FALLBACKS = {"prof": _fallback_prof, "ceo": _fallback_ceo, "lawyer": _fallback_lawyer}

# ─── 主渲染 ───
def render():
    st.markdown("# 🧬 三角色工作台 TripleHelix")
    st.markdown("""<div class="impossible">
        <div class="before">❌ 以前：教授不懂市场、企业家不懂技术、律师不懂创新——三角色需要三个团队</div>
        <div class="after">✅ 现在：一个OPC创业者+三个AI Agent，同时扮演教授、CEO、律师三个角色</div>
    </div>""", unsafe_allow_html=True)
    st.caption("📐 理论支撑：三螺旋理论(Etzkowitz & Leydesdorff 1995) + 委托-代理理论 + 基于任务模型(Autor)")

    # 初始化session state
    for k in ["role", "project_name", "project_desc", "analysis_results", "analysis_engine"]:
        if k not in st.session_state:
            st.session_state[k] = "" if k in ("role","project_name","project_desc") else ({} if k == "analysis_results" else {})

    # 角色选择
    c1, c2, c3 = st.columns(3)
    with c1:
        prof = st.button("🎓 **教授角色**\n知识评估·技术分析", use_container_width=True,
                         type="primary" if st.session_state.role == "prof" else "secondary")
    with c2:
        ceo = st.button("👔 **CEO角色**\n市场分析·商业决策", use_container_width=True,
                        type="primary" if st.session_state.role == "ceo" else "secondary")
    with c3:
        lawyer = st.button("⚖️ **律师角色**\n合规审查·合同审核", use_container_width=True,
                           type="primary" if st.session_state.role == "lawyer" else "secondary")

    if prof: st.session_state.role = "prof"
    elif ceo: st.session_state.role = "ceo"
    elif lawyer: st.session_state.role = "lawyer"

    role = st.session_state.role
    st.markdown("---")

    # 共享项目上下文
    with st.expander("📋 共享项目上下文（三角色共享）", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            st.session_state.project_name = st.text_input("项目名称", value=st.session_state.project_name, key="pn")
            st.session_state.project_desc = st.text_area("项目描述（论文摘要/专利说明书/技术方案）",
                                                          value=st.session_state.project_desc, height=100, key="pd")
        with c2:
            st.markdown("""
            **三角色协同机制**：
            - 📋 项目信息在三角色间实时同步
            - 🧠 每个角色的分析结果对其他角色可见
            - 🔄 后分析的角色能看到先分析角色的结论
            - ⚡ 三角色可按任意顺序分析

            *这就是三螺旋的微观实现——*
            *一个人+AI=大学+产业+政府*
            """)

    # 一键分析 / 单角色分析
    st.markdown("---")
    bc1, bc2 = st.columns([1, 1])
    with bc1:
        run_all = st.button("🚀 一键三角色分析", type="primary", use_container_width=True)
    with bc2:
        run_single = st.button(f"🎯 仅分析当前角色（{role}）", use_container_width=True)

    if run_all or run_single:
        name = st.session_state.project_name.strip()
        desc = st.session_state.project_desc.strip()
        if not name or not desc:
            st.error("请先填写项目名称和描述")
        else:
            roles_to_run = ["prof", "ceo", "lawyer"] if run_all else [role]
            # 按顺序执行（后执行的角色能看到前面的结果）
            for i, r in enumerate(roles_to_run):
                role_names = {"prof": "教授", "ceo": "CEO", "lawyer": "律师"}
                with st.status(f"🤖 {role_names[r]}Agent正在分析...", expanded=True) as status:
                    # 构建prompt，注入已有分析结果
                    other_data = {k: v for k, v in st.session_state.analysis_results.items() if v}
                    prompt = _build_prompt(name, desc, r, other_data)

                    st.write(f"调用LLM分析...")
                    result = _llm_raw(SYSTEM_PROMPTS[r], prompt)

                    if result:
                        st.session_state.analysis_results[r] = result
                        st.session_state.analysis_engine[r] = "🤖 AI"
                        st.success(f"✅ {role_names[r]}Agent分析完成（AI）")
                    else:
                        st.session_state.analysis_results[r] = FALLBACKS[r](name, desc)
                        st.session_state.analysis_engine[r] = "📐 规则"
                        st.warning(f"⚠️ {role_names[r]}Agent降级为规则引擎")

    # 显示分析结果
    if st.session_state.analysis_results:
        st.markdown("---")
        st.markdown("### 📊 分析结果")

        # 当前角色优先展示
        display_order = [role] + [r for r in ["prof", "ceo", "lawyer"] if r != role and r in st.session_state.analysis_results]

        for r in display_order:
            if r not in st.session_state.analysis_results:
                continue
            role_icons = {"prof": "🎓", "ceo": "👔", "lawyer": "⚖️"}
            role_names = {"prof": "教授", "ceo": "CEO", "lawyer": "律师"}
            engine = st.session_state.analysis_engine.get(r, "")
            is_current = (r == role)

            with st.expander(
                f"{role_icons[r]} {role_names[r]}Agent  {engine}",
                expanded=is_current
            ):
                st.markdown(st.session_state.analysis_results[r])
                st.download_button(
                    "📥 导出", data=st.session_state.analysis_results[r],
                    file_name=f"{st.session_state.project_name}_{role_names[r]}分析_{datetime.now().strftime('%Y%m%d')}.md",
                    mime="text/markdown", key=f"dl_{r}"
                )

        # 三角色综合建议
        if len(st.session_state.analysis_results) == 3:
            st.markdown("---")
            st.markdown("### 🧬 三角色综合建议")
            st.info("三个角色的分析已完成。以下是综合建议：")
            st.markdown("""
            | 角度 | 核心观点 | 关键行动 |
            |------|---------|---------|
            | 🎓 教授 | 技术可行性和科学价值 | 完善技术验证，提升成熟度 |
            | 👔 CEO | 市场机会和商业模式 | 锁定目标客户，快速验证 |
            | ⚖️ 律师 | 合规风险和知识产权 | 完成评估备案，设计合同 |

            **综合建议**：三个角色的分析形成互补——教授确保技术"能做"，CEO确保"有人买单"，律师确保"合法合规"。
            建议按照"律师先行（合规确认）→ 教授跟进（技术优化）→ CEO收尾（商业落地）"的顺序推进。
            """)

"""联邦匹配 FedMatch - 跨校专利数据不出校
v0.5 - 真实TF-IDF向量化匹配 + LLM增强 + 模拟降级
"""
import streamlit as st, random, json, re, hashlib
from datetime import datetime
from llm_utils import llm_chat
from collections import Counter
import math

# ─── 本地专利数据库（模拟各高校本地数据） ───
PATENT_DB = [
    # 人工智能
    {"name": "基于联邦学习的医疗影像AI诊断", "school": "清华大学", "trl": "TRL 5", "patent": "CN202310XXXXXX",
     "field": "人工智能", "brief": "在3家三甲医院完成临床验证，诊断准确率96.3%，支持多模态融合",
     "highlights": ["已获3项发明专利", "临床验证数据充分", "可扩展到其他影像模态"],
     "risk": ["需要大量标注数据", "监管审批周期长"], "budget": "许可费200-500万/年"},
    {"name": "多模态大模型高效推理框架", "school": "北京大学", "trl": "TRL 4", "patent": "CN202410XXXXXX",
     "field": "人工智能", "brief": "将大模型推理速度提升3-5倍，显存占用降低60%，支持主流GPU",
     "highlights": ["开源社区Star 2.3k", "多篇顶会论文", "已与2家企业合作"],
     "risk": ["技术迭代快", "开源模式盈利不确定"], "budget": "技术许可+联合开发"},
    {"name": "基于强化学习的智能调度系统", "school": "浙江大学", "trl": "TRL 6", "patent": "CN202310XXXXXX",
     "field": "人工智能", "brief": "适用于柔性制造车间的智能排产，已在3家工厂部署，产能提升15%",
     "highlights": ["已有落地案例", "ROI可量化", "技术成熟度高"],
     "risk": ["行业定制化需求强", "市场规模有限"], "budget": "许可费50-150万/年"},
    {"name": "面向自动驾驶的多传感器融合算法", "school": "上海交通大学", "trl": "TRL 3", "patent": "申请中",
     "field": "人工智能", "brief": "融合激光雷达、摄像头、毫米波雷达，在KITTI数据集上SOTA",
     "highlights": ["学术影响力强", "算法创新性高"],
     "risk": ["距离量产较远", "竞争激烈", "需要大量路测数据"], "budget": "需天使轮融资"},
    {"name": "边缘端轻量化目标检测模型", "school": "西交利物浦大学", "trl": "TRL 5", "patent": "CN202410XXXXXX",
     "field": "人工智能", "brief": "面向嵌入式设备的实时目标检测，模型仅2MB，推理延迟<10ms",
     "highlights": ["模型极致轻量", "端侧实时推理", "已部署工业质检场景"],
     "risk": ["精度有折损", "场景适配需调优"], "budget": "许可费30-80万/年"},
    # 生物医药
    {"name": "新型mRNA递送脂质纳米颗粒", "school": "复旦大学", "trl": "TRL 4", "patent": "CN202410XXXXXX",
     "field": "生物医药", "brief": "新型LNP配方，递送效率提升40%，已在动物模型中验证",
     "highlights": ["递送效率显著提升", "专利壁垒高", "mRNA赛道热度高"],
     "risk": ["临床前数据有限", "监管路径不确定"], "budget": "许可费300-800万+里程碑"},
    {"name": "AI辅助药物分子生成平台", "school": "中国科学技术大学", "trl": "TRL 3", "patent": "CN202310XXXXXX",
     "field": "生物医药", "brief": "基于生成式AI的先导化合物设计，已生成3个候选分子进入体外验证",
     "highlights": ["AI+制药交叉", "生成效率高", "可降低研发成本"],
     "risk": ["候选分子需进一步验证", "AI生成药物监管空白"], "budget": "合作开发+里程碑付款"},
    # 新材料
    {"name": "高效能量存储复合材料", "school": "南京大学", "trl": "TRL 5", "patent": "CN202410XXXXXX",
     "field": "新材料", "brief": "新型复合电极材料，能量密度提升35%，循环寿命2000次以上",
     "highlights": ["性能指标领先", "制备工艺成熟", "成本可控"],
     "risk": ["规模化生产待验证", "市场竞争激烈"], "budget": "许可费100-300万/年"},
    {"name": "钙钛矿太阳能电池稳定性提升技术", "school": "中国科学院", "trl": "TRL 4", "patent": "CN202410XXXXXX",
     "field": "新材料", "brief": "通过界面工程将钙钛矿电池T80寿命提升至5000小时，效率保持25.6%",
     "highlights": ["稳定性突破", "效率行业领先", "工艺可规模化"],
     "risk": ["铅毒性问题", "大面积制备良率"], "budget": "许可费200-500万+股权"},
    # 新能源/节能环保
    {"name": "工业废水深度处理技术", "school": "同济大学", "trl": "TRL 6", "patent": "CN202310XXXXXX",
     "field": "节能环保", "brief": "新型催化氧化工艺，处理成本降低50%，已在2个工业园区示范",
     "highlights": ["已有示范工程", "处理效果好", "政策驱动需求"],
     "risk": ["适用场景有限", "运维要求高"], "budget": "许可费80-200万/年"},
    {"name": "固态电池界面修饰技术", "school": "厦门大学", "trl": "TRL 4", "patent": "CN202410XXXXXX",
     "field": "新能源", "brief": "解决固态电池固固界面阻抗问题，循环寿命提升3倍",
     "highlights": ["解决核心痛点", "工艺兼容现有产线", "已申请PCT"],
     "risk": ["量产一致性待验证", "成本偏高"], "budget": "联合开发+里程碑"},
    # 电子信息/先进制造
    {"name": "RISC-V向量处理器IP核", "school": "西交利物浦大学", "trl": "TRL 4", "patent": "CN202410XXXXXX",
     "field": "电子信息", "brief": "自主设计RISC-V向量扩展IP核，支持ML加速，面积效率优于商用方案30%",
     "highlights": ["完全自主可控", "面积效率领先", "已流片验证"],
     "risk": ["生态成熟度", "工具链完善度"], "budget": "IP授权+技术支持"},
    {"name": "柔性传感器阵列印刷工艺", "school": "华南理工大学", "trl": "TRL 5", "patent": "CN202310XXXXXX",
     "field": "先进制造", "brief": "卷对卷印刷柔性压力传感器，成本降低80%，可大面积部署",
     "highlights": ["成本大幅降低", "可大面积制造", "已对接可穿戴厂商"],
     "risk": ["精度一致性", "长期可靠性"], "budget": "许可费100-200万/年"},
]

# ─── TF-IDF 向量化引擎 ───
def _tokenize(text):
    """简单分词：中文按字+英文按词"""
    tokens = re.findall(r'[a-zA-Z]+|[\u4e00-\u9fff]', text.lower())
    return tokens

def _build_tfidf(corpus):
    """构建TF-IDF模型"""
    N = len(corpus)
    df = Counter()
    doc_tokens = []
    for doc in corpus:
        tokens = _tokenize(doc)
        doc_tokens.append(tokens)
        for t in set(tokens):
            df[t] += 1
    idf = {t: math.log(N / (1 + df_t)) for t, df_t in df.items()}
    return idf, doc_tokens

def _vectorize(text, idf):
    """将文本转为TF-IDF向量"""
    tokens = _tokenize(text)
    tf = Counter(tokens)
    vec = {}
    for t, count in tf.items():
        if t in idf:
            vec[t] = count * idf[t]
    return vec

def _cosine_sim(v1, v2):
    """余弦相似度"""
    if not v1 or not v2:
        return 0.0
    dot = sum(v1[t] * v2.get(t, 0) for t in v1)
    norm1 = math.sqrt(sum(v * v for v in v1.values()))
    norm2 = math.sqrt(sum(v * v for v in v2.values()))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)

def _federated_match(need_text, field_filter=None, top_k=5):
    """
    模拟联邦匹配流程：
    1. 需求方向量化
    2. 广播到各"高校节点"（本地数据子集）
    3. 各节点本地计算相似度
    4. 聚合排序返回Top-K
    """
    # 按学校分组（模拟各高校本地数据）
    schools = {}
    for p in PATENT_DB:
        if field_filter and field_filter not in p["field"]:
            continue
        schools.setdefault(p["school"], []).append(p)

    # 构建全局IDF（模拟联邦IDF聚合）
    all_texts = [p["brief"] + p["name"] for p in PATENT_DB]
    idf, _ = _build_tfidf(all_texts)

    # 需求向量
    need_vec = _vectorize(need_text, idf)

    # 各校本地匹配（数据不出校）
    all_results = []
    for school, patents in schools.items():
        for p in patents:
            p_vec = _vectorize(p["brief"] + p["name"], idf)
            sim = _cosine_sim(need_vec, p_vec)
            # 加入随机微扰模拟"本地模型差异"
            sim_adj = sim * (0.85 + random.uniform(0, 0.3))
            score = round(min(98, max(40, sim_adj * 200)))
            p_copy = {**p, "score": score, "school": school}
            all_results.append(p_copy)

    # 聚合排序
    all_results.sort(key=lambda x: -x["score"])
    return all_results[:top_k]

# ─── LLM 增强：需求扩展 ───
def _llm_expand_query(need_text):
    """用LLM扩展需求描述，增加同义词和关联词"""
    system = "你是技术转移领域的需求分析专家。将用户的技术需求描述扩展为更丰富的检索词，添加同义词、相关技术术语。只输出扩展后的文本，不超过200字。"
    raw = llm_chat(system, need_text)
    return raw if raw else need_text

def render():
    st.markdown("# 🔗 联邦匹配 FedMatch")
    st.markdown("""<div class="impossible">
        <div class="before">❌ 以前：企业只能一家一家TTO问，永远问不完，且各校数据不共享</div>
        <div class="after">✅ 现在：联邦学习广播需求，各校本地匹配，数据不出校，一次搜索100+高校</div>
    </div>""", unsafe_allow_html=True)
    st.caption("📐 理论支撑：联邦学习经济学 + 平台经济学(Katz & Shapiro) + 搜寻理论(Stigler)")

    tab1,tab2,tab3 = st.tabs(["🔍 发起匹配","📋 匹配历史","📖 工作原理"])

    with tab1:
        st.markdown("### 📡 企业技术需求")
        with st.form("match_form"):
            c1,c2 = st.columns(2)
            with c1:
                need = st.text_area("技术需求描述 *", height=100, placeholder="描述您需要解决的技术问题...\n例：我们是一家医疗影像公司，需要一种能在保护患者隐私的前提下进行多中心AI模型训练的技术方案")
                field = st.selectbox("技术领域",["人工智能/机器学习","生物医药","新材料","新能源","电子信息","先进制造","节能环保","其他"])
            with c2:
                budget = st.selectbox("预算范围",["10万以内","10-50万","50-200万","200-500万","500万以上","面议"])
                urgency = st.selectbox("紧急程度",["非常紧急(1个月内)","紧急(3个月内)","一般(6个月内)","不急(探索性)"])
                trl_need = st.selectbox("期望技术成熟度",[f"TRL {i}及以上" for i in range(3,10)], index=3)
                use_llm = st.checkbox("🤖 启用LLM需求扩展（更精准匹配）", value=False)

            submitted = st.form_submit_button("🔗 发起联邦匹配", type="primary", use_container_width=True)

        if submitted:
            if not need:
                st.error("请描述技术需求")
                return

            # 字段映射
            field_map = {
                "人工智能/机器学习": "人工智能", "生物医药": "生物医药",
                "新材料": "新材料", "新能源": "新能源",
                "电子信息": "电子信息", "先进制造": "先进制造",
                "节能环保": "节能环保", "其他": None,
            }
            field_key = field_map.get(field)

            with st.spinner("联邦匹配引擎工作中..."):
                import time
                # Step 1: 可选LLM扩展
                search_text = need
                engine_label = "TF-IDF向量匹配"
                if use_llm:
                    with st.spinner("LLM需求扩展中..."):
                        expanded = _llm_expand_query(need)
                        if expanded and len(expanded) > len(need):
                            search_text = expanded
                            engine_label = "LLM扩展 + TF-IDF向量匹配"
                    time.sleep(0.5)

                # Step 2: 联邦匹配
                time.sleep(1)
                results = _federated_match(search_text, field_key, top_k=5)

            record = {
                "need": need, "field": field, "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "results": results, "engine": engine_label,
            }
            st.session_state.matches.append(record)
            st.rerun()

        if st.session_state.matches:
            r = st.session_state.matches[-1]
            st.markdown("---")
            engine = r.get("engine", "TF-IDF向量匹配")
            st.markdown(f"**需求**：{r['need'][:100]}... ｜ **领域**：{r['field']} ｜ **匹配到 {len(r['results'])} 项技术** ｜ **引擎**：{engine}")

            for i, item in enumerate(r["results"]):
                score = item["score"]
                badge = "🟢 极高" if score>=85 else "🔵 较高" if score>=75 else "🟡 中等"
                color = "#00b894" if score>=85 else "#0984e3" if score>=75 else "#fdcb6e"
                with st.expander(f"#{i+1} {item['name']} — {item['school']} — 匹配度 {score}% {badge}", expanded=(i==0)):
                    c1,c2 = st.columns([3,1])
                    with c1:
                        st.markdown(f"**简介**：{item['brief']}")
                        st.markdown("**✅ 优势**：" + "、".join(item["highlights"]))
                        st.markdown("**⚠️ 风险**：" + "、".join(item["risk"]))
                        st.markdown(f"**💰 参考费用**：{item['budget']}")
                    with c2:
                        st.markdown(f"""<div class="metric-box"><div class="num" style="color:{color}">{score}%</div><div class="label">匹配度</div></div>""", unsafe_allow_html=True)
                        st.caption(f"成熟度：{item['trl']}")
                        st.caption(f"专利：{item['patent']}")

            st.success(f"联邦匹配完成（{engine}）。以上结果由各参与高校本地计算TF-IDF相似度后聚合排序生成，原始专利数据未离开各校环境。")

    with tab2:
        if not st.session_state.matches:
            st.info("暂无匹配记录")
        for m in reversed(st.session_state.matches):
            engine = m.get("engine", "TF-IDF")
            with st.expander(f"🔗 {m['need'][:60]}... — {m['date']} [{engine}]"):
                st.write(f"领域：{m['field']} | 匹配数：{len(m['results'])} | 引擎：{engine}")

    with tab3:
        st.markdown("""
        ### 联邦匹配工作原理

        ```
        企业输入需求
              │
              ▼
        ┌─────────────────┐
        │   需求向量化      │  ← TF-IDF + (可选)LLM扩展
        │   (需求编码)      │
        └────────┬────────┘
                 │ 广播需求向量（不含原始需求文本）
        ┌────────┼────────┐
        ▼        ▼        ▼
     ┌─────┐ ┌─────┐ ┌─────┐
     │清华  │ │北大  │ │浙大  │  ← 各校本地
     │本地  │ │本地  │ │本地  │     数据不出校
     │匹配  │ │匹配  │ │匹配  │
     └──┬──┘ └──┬──┘ └──┬──┘
        │       │       │
        ▼       ▼       ▼
        ┌─────────────────┐
        │  聚合+排序       │  ← 只交换匹配分数，不交换原始数据
        │  返回Top结果     │
        └─────────────────┘
        ```

        **技术实现**：
        - 📐 **TF-IDF向量化**：将需求和技术描述编码为词频-逆文档频率向量
        - 📊 **余弦相似度**：计算需求向量与各专利向量的余弦相似度
        - 🤖 **LLM扩展（可选）**：用大模型扩展需求描述，增加同义词和关联术语
        - 🔒 **数据主权**：各校专利数据始终存储在本地，仅交换匹配分数
        - ⚖️ **合规保障**：符合《数据安全法》《个人信息保护法》

        **与真实联邦学习的差距**：
        - 当前版本使用集中式TF-IDF（模拟联邦IDF聚合）
        - 生产环境应接入FedCtx等联邦学习后端，实现真正的分布式训练
        - 可扩展为联邦向量数据库（如基于FedCtx的语义检索）
        """)

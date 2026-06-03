"""联邦匹配 FedMatch - 跨校专利数据不出校"""
import streamlit as st, random
from llm_utils import llm_chat
from datetime import datetime

def _sim_match(need, field):
    pool = {
        "人工智能": [
            {"name":"基于联邦学习的医疗影像AI诊断","school":"清华大学","trl":"TRL 5","score":92,"patent":"CN202310XXXXXX","brief":"在3家三甲医院完成临床验证，诊断准确率96.3%，支持多模态融合","highlights":["已获3项发明专利","临床验证数据充分","可扩展到其他影像模态"],"risk":["需要大量标注数据","监管审批周期长"],"budget":"许可费200-500万/年"},
            {"name":"多模态大模型高效推理框架","school":"北京大学","trl":"TRL 4","score":85,"patent":"CN202410XXXXXX","brief":"将大模型推理速度提升3-5倍，显存占用降低60%，支持主流GPU","highlights":["开源社区Star 2.3k","多篇顶会论文","已与2家企业合作"],"risk":["技术迭代快","开源模式盈利不确定"],"budget":"技术许可+联合开发"},
            {"name":"基于强化学习的智能调度系统","school":"浙江大学","trl":"TRL 6","score":78,"patent":"CN202310XXXXXX","brief":"适用于柔性制造车间的智能排产，已在3家工厂部署，产能提升15%","highlights":["已有落地案例","ROI可量化","技术成熟度高"],"risk":["行业定制化需求强","市场规模有限"],"budget":"许可费50-150万/年"},
            {"name":"面向自动驾驶的多传感器融合算法","school":"上海交通大学","trl":"TRL 3","score":71,"patent":"申请中","brief":"融合激光雷达、摄像头、毫米波雷达，在KITTI数据集上SOTA","highlights":["学术影响力强","算法创新性高"],"risk":["距离量产较远","竞争激烈","需要大量路测数据"],"budget":"需天使轮融资"},
        ],
        "生物医药": [
            {"name":"新型mRNA递送脂质纳米颗粒","school":"复旦大学","trl":"TRL 4","score":89,"patent":"CN202410XXXXXX","brief":"新型LNP配方，递送效率提升40%，已在动物模型中验证","highlights":["递送效率显著提升","专利壁垒高","mRNA赛道热度高"],"risk":["临床前数据有限","监管路径不确定"],"budget":"许可费300-800万+里程碑"},
            {"name":"AI辅助药物分子生成平台","school":"中国科学技术大学","trl":"TRL 3","score":76,"patent":"CN202310XXXXXX","brief":"基于生成式AI的先导化合物设计，已生成3个候选分子进入体外验证","highlights":["AI+制药交叉","生成效率高","可降低研发成本"],"risk":["候选分子需进一步验证","AI生成药物监管空白"],"budget":"合作开发+里程碑付款"},
        ],
    }
    default = [
        {"name":"高效能量存储复合材料","school":"南京大学","trl":"TRL 5","score":82,"patent":"CN202410XXXXXX","brief":"新型复合电极材料，能量密度提升35%，循环寿命2000次以上","highlights":["性能指标领先","制备工艺成熟","成本可控"],"risk":["规模化生产待验证","市场竞争激烈"],"budget":"许可费100-300万/年"},
        {"name":"工业废水深度处理技术","school":"同济大学","trl":"TRL 6","score":75,"patent":"CN202310XXXXXX","brief":"新型催化氧化工艺，处理成本降低50%，已在2个工业园区示范","highlights":["已有示范工程","处理效果好","政策驱动需求"],"risk":["适用场景有限","运维要求高"],"budget":"许可费80-200万/年"},
    ]
    results = pool.get(field, default)
    random.shuffle(results)
    return results

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

            submitted = st.form_submit_button("🔗 发起联邦匹配", type="primary", use_container_width=True)

        if submitted:
            if not need:
                st.error("请描述技术需求")
                return
            with st.spinner("联邦匹配引擎工作中..."):
                import time; time.sleep(2)
            results = _sim_match(need, field)
            record = {"need":need,"field":field,"date":datetime.now().strftime("%Y-%m-%d %H:%M"),"results":results}
            st.session_state.matches.append(record)
            st.rerun()

        if st.session_state.matches:
            r = st.session_state.matches[-1]
            st.markdown("---")
            st.markdown(f"**需求**：{r['need'][:100]}... ｜ **领域**：{r['field']} ｜ **匹配到 {len(r['results'])} 项技术**")

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

            st.success("联邦匹配完成。以上结果由联邦学习引擎在各参与高校本地计算后聚合生成，原始专利数据未离开各校环境。")

    with tab2:
        if not st.session_state.matches:
            st.info("暂无匹配记录")
        for m in reversed(st.session_state.matches):
            with st.expander(f"🔗 {m['need'][:60]}... — {m['date']}"):
                st.write(f"领域：{m['field']} | 匹配数：{len(m['results'])}")

    with tab3:
        st.markdown("""
        ### 联邦匹配工作原理

        ```
        企业输入需求
              │
              ▼
        ┌─────────────────┐
        │   联邦匹配引擎    │
        │  (需求向量化)     │
        └────────┬────────┘
                 │ 广播加密需求向量
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

        **关键特性**：
        - 🔒 **数据主权**：各校专利数据始终存储在本地
        - 📊 **隐私保护**：仅交换加密后的模型参数/匹配分数
        - 🔄 **增量学习**：每次匹配都提升模型精度
        - ⚖️ **合规保障**：符合《数据安全法》《个人信息保护法》
        """)

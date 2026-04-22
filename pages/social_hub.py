"""社交传播交易 SocialHub - 网络效应驱动的技术转移生态
v0.3 - 社交网络 + 内容传播 + 交易撮合
"""
import streamlit as st, json, subprocess, re, time, random
from datetime import datetime, timedelta

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

# ─── 初始化Session State ───
def _init_state():
    defaults = {
        "social_feed": [],
        "my_posts": [],
        "deals": [],
        "connections": [],
        "notifications": [],
        "social_profile": {
            "name": "张三",
            "title": "技术转移OPC",
            "institution": "某大学TTO",
            "field": "人工智能",
            "bio": "专注AI领域技术转移，已促成12项成果转化",
            "followers": random.randint(50, 500),
            "following": random.randint(20, 200),
            "deals_done": random.randint(3, 15),
            "rating": round(random.uniform(4.2, 4.9), 1),
        },
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # 预置一些社交动态
    if not st.session_state.social_feed:
        st.session_state.social_feed = [
            {
                "author": "李明 @清华TTO",
                "avatar": "🧑‍🔬",
                "time": (datetime.now() - timedelta(hours=2)).strftime("%H:%M"),
                "content": "刚刚完成一项联邦学习专利的评估，盲盒评分82分！AI评估报告质量超出预期，买方反馈非常积极。这就是Arrow信息悖论的解决方案。 #盲盒评估 #联邦学习",
                "likes": random.randint(15, 80),
                "comments": random.randint(3, 20),
                "shares": random.randint(2, 10),
                "type": "achievement",
            },
            {
                "author": "王芳 @浙大创新中心",
                "avatar": "👩‍💼",
                "time": (datetime.now() - timedelta(hours=5)).strftime("%H:%M"),
                "content": "分享一个案例：用场景翻译功能把一篇Nature论文翻译成了投资人版和CEO版，投资人当天就约了会议。以前这个翻译工作至少要花一周。 #场景翻译 #效率提升",
                "likes": random.randint(30, 120),
                "comments": random.randint(8, 35),
                "shares": random.randint(10, 40),
                "type": "case",
            },
            {
                "author": "陈刚 @中科院苏州医工所",
                "avatar": "👨‍🔬",
                "time": (datetime.now() - timedelta(hours=8)).strftime("%H:%M"),
                "content": "三角色工作台太强了！教授Agent指出了我们技术的一个关键缺陷，CEO Agent帮我们重新定位了目标市场，律师Agent提醒了国有资产评估的合规要求。一个人干三个团队的活。 #三角色 #OPC",
                "likes": random.randint(50, 200),
                "comments": random.randint(15, 50),
                "shares": random.randint(20, 60),
                "type": "review",
            },
            {
                "author": "赵薇 @上交大技术转移中心",
                "avatar": "👩‍💻",
                "time": (datetime.now() - timedelta(hours=12)).strftime("%H:%M"),
                "content": "技术雷达扫描发现我们的核心专利窗口期只剩18个月了！大厂的替代方案进展很快。已启动加速转化计划。 #技术雷达 #紧迫",
                "likes": random.randint(20, 90),
                "comments": random.randint(5, 25),
                "shares": random.randint(5, 15),
                "type": "alert",
            },
            {
                "author": "刘洋 @北大科技开发部",
                "avatar": "🧑‍💻",
                "time": (datetime.now() - timedelta(days=1)).strftime("%m-%d %H:%M"),
                "content": "求合作：手头一项mRNA递送技术（TRL4，Nature子刊），寻求生物医药企业合作开发。已生成盲盒评估报告和投资人版翻译，可分享。有意者私信。 #求合作 #生物医药",
                "likes": random.randint(10, 50),
                "comments": random.randint(8, 30),
                "shares": random.randint(3, 12),
                "type": "collab",
            },
        ]

    # 预置一些交易
    if not st.session_state.deals:
        st.session_state.deals = [
            {
                "id": "D001",
                "tech": "基于联邦学习的医疗影像AI",
                "seller": "张三 @清华TTO",
                "buyer": "XX医疗科技",
                "stage": "negotiating",
                "stage_label": "🤝 谈判中",
                "amount": "300万/年",
                "model": "排他许可",
                "created": (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d"),
                "next_action": "本周五合同条款终审",
                "progress": 65,
                "timeline": [
                    {"date": "03-20", "event": "盲盒评估完成", "status": "done"},
                    {"date": "03-25", "event": "买方查看评估报告", "status": "done"},
                    {"date": "04-01", "event": "首次技术交流会", "status": "done"},
                    {"date": "04-10", "event": "概念验证启动", "status": "done"},
                    {"date": "04-18", "event": "商务条款谈判", "status": "current"},
                    {"date": "04-25", "event": "合同签署", "status": "pending"},
                    {"date": "05-01", "event": "首期许可费到账", "status": "pending"},
                ],
            },
            {
                "id": "D002",
                "tech": "新型钙钛矿太阳能电池制备工艺",
                "seller": "王芳 @浙大材料学院",
                "buyer": "XX新能源",
                "stage": "matching",
                "stage_label": "🔗 匹配中",
                "amount": "待定",
                "model": "技术许可+联合开发",
                "created": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
                "next_action": "等待买方反馈",
                "progress": 30,
                "timeline": [
                    {"date": "04-16", "event": "联邦匹配命中", "status": "done"},
                    {"date": "04-17", "event": "盲盒评估报告生成", "status": "done"},
                    {"date": "04-18", "event": "场景翻译（CEO版）发送", "status": "current"},
                    {"date": "??", "event": "买方回复意向", "status": "pending"},
                ],
            },
            {
                "id": "D003",
                "tech": "AI辅助药物分子筛选平台",
                "seller": "陈刚 @中科大",
                "buyer": "XX制药",
                "stage": "completed",
                "stage_label": "✅ 已成交",
                "amount": "500万+里程碑",
                "model": "独占许可",
                "created": (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d"),
                "next_action": "跟踪里程碑付款",
                "progress": 100,
                "timeline": [
                    {"date": "02-15", "event": "匹配成功", "status": "done"},
                    {"date": "02-28", "event": "评估+翻译完成", "status": "done"},
                    {"date": "03-10", "event": "技术交流会", "status": "done"},
                    {"date": "03-20", "event": "合同签署", "status": "done"},
                    {"date": "03-25", "event": "首期款到账", "status": "done"},
                ],
            },
        ]

    # 预置连接
    if not st.session_state.connections:
        st.session_state.connections = [
            {"name": "李明", "institution": "清华大学TTO", "field": "人工智能", "status": "connected", "deals": 5},
            {"name": "王芳", "institution": "浙江大学创新中心", "field": "新材料", "status": "connected", "deals": 3},
            {"name": "陈刚", "institution": "中科院苏州医工所", "field": "生物医药", "status": "connected", "deals": 8},
            {"name": "赵薇", "institution": "上交大技术转移中心", "field": "电子信息", "status": "pending", "deals": 0},
            {"name": "刘洋", "institution": "北大科技开发部", "field": "生物医药", "status": "connected", "deals": 2},
        ]


def render():
    _init_state()

    st.markdown("# 🌐 社交传播交易 SocialHub")
    st.markdown("""<div class="impossible">
        <div class="before">❌ 以前：技术转移是"孤岛"——OPC之间不交流、信息不流通、交易靠人脉</div>
        <div class="after">✅ 现在：社交网络连接OPC社区、内容传播放大技术影响力、交易撮合降低成交摩擦</div>
    </div>""", unsafe_allow_html=True)
    st.caption("📐 理论支撑：网络效应(Metcalfe) + 双边市场(Rochet & Tirole) + 信号理论(Spence) + 声誉机制 + 社会资本(Bourdieu)")

    # 个人资料卡片
    p = st.session_state.social_profile
    st.markdown(f"""
    <div class="card" style="display:flex;align-items:center;gap:1rem;flex-wrap:wrap">
        <div style="font-size:2.5rem">🧑‍💼</div>
        <div style="flex:1;min-width:200px">
            <div style="font-weight:700;font-size:1.1rem">{p['name']} <span style="color:var(--muted);font-weight:400;font-size:.85rem">{p['title']} · {p['institution']}</span></div>
            <div style="color:var(--muted);font-size:.85rem;margin-top:.2rem">{p['bio']}</div>
        </div>
        <div style="display:flex;gap:1.5rem;flex-wrap:wrap">
            <div style="text-align:center"><div style="font-weight:700;font-size:1.2rem">{p['followers']}</div><div style="font-size:.7rem;color:var(--muted)">关注者</div></div>
            <div style="text-align:center"><div style="font-weight:700;font-size:1.2rem">{p['following']}</div><div style="font-size:.7rem;color:var(--muted)">关注中</div></div>
            <div style="text-align:center"><div style="font-weight:700;font-size:1.2rem">{p['deals_done']}</div><div style="font-size:.7rem;color:var(--muted)">成交</div></div>
            <div style="text-align:center"><div style="font-weight:700;font-size:1.2rem;color:#f39c12">⭐ {p['rating']}</div><div style="font-size:.7rem;color:var(--muted)">信誉分</div></div>
        </div>
    </div>""", unsafe_allow_html=True)

    # 四个Tab
    tab1, tab2, tab3, tab4 = st.tabs(["📰 动态广场", "✍️ 发布内容", "🤝 交易管理", "👥 人脉网络"])

    # ═══════════════════════════════════════
    # Tab1: 动态广场
    # ═══════════════════════════════════════
    with tab1:
        st.markdown("### 📰 OPC社区动态")

        # 筛选
        c1, c2 = st.columns([3, 1])
        with c1:
            filter_type = st.selectbox("筛选类型", ["全部", "🏆 成果展示", "📋 案例分享", "💬 使用心得", "🆘 求合作", "📢 行业资讯"], key="feed_filter")
        with c2:
            st.markdown("<div style='height:2.6rem'></div>", unsafe_allow_html=True)
            if st.button("🔄 刷新", use_container_width=True):
                st.rerun()

        type_map = {
            "全部": None, "🏆 成果展示": "achievement", "📋 案例分享": "case",
            "💬 使用心得": "review", "🆘 求合作": "collab", "📢 行业资讯": "alert",
        }
        filtered = st.session_state.social_feed
        if type_map.get(filter_type):
            filtered = [f for f in filtered if f.get("type") == type_map[filter_type]]

        for post in filtered:
            type_badge = {
                "achievement": "🏆 成果", "case": "📋 案例", "review": "💬 心得",
                "collab": "🆘 合作", "alert": "📢 资讯",
            }.get(post.get("type", ""), "📝")

            st.markdown(f"""
            <div class="card">
                <div style="display:flex;align-items:center;gap:.5rem;margin-bottom:.5rem">
                    <span style="font-size:1.5rem">{post['avatar']}</span>
                    <div>
                        <span style="font-weight:600;font-size:.9rem">{post['author']}</span>
                        <span style="color:var(--muted);font-size:.75rem;margin-left:.5rem">{post['time']}</span>
                    </div>
                    <span style="margin-left:auto;background:#f0f4ff;color:#0984e3;padding:.1rem .5rem;border-radius:999px;font-size:.7rem">{type_badge}</span>
                </div>
                <div style="font-size:.9rem;line-height:1.6">{post['content']}</div>
                <div style="display:flex;gap:1.5rem;margin-top:.8rem;color:var(--muted);font-size:.8rem">
                    <span>❤️ {post['likes']}</span>
                    <span>💬 {post['comments']}</span>
                    <span>🔄 {post['shares']}</span>
                </div>
            </div>""", unsafe_allow_html=True)

    # ═══════════════════════════════════════
    # Tab2: 发布内容
    # ═══════════════════════════════════════
    with tab2:
        st.markdown("### ✍️ 发布技术动态")

        with st.form("publish_form"):
            post_type = st.selectbox("动态类型", [
                "🏆 成果展示 — 分享评估/匹配/成交成果",
                "📋 案例分享 — 分享技术转移成功案例",
                "💬 使用心得 — 分享平台使用体验",
                "🆘 求合作 — 发布技术合作需求",
                "📢 行业资讯 — 分享行业动态和政策",
            ])
            content = st.text_area("内容", placeholder="分享你的技术转移经验、成果或需求...\n\n支持 #话题标签", height=150)
            attach = st.selectbox("关联内容（可选）", ["无", "关联盲盒评估报告", "关联联邦匹配结果", "关联场景翻译", "关联交易"])
            c1, c2 = st.columns(2)
            with c1:
                audience = st.multiselect("可见范围", ["👥 全部OPC", "🔒 仅关注者", "🎯 指定领域"], default=["👥 全部OPC"])
            with c2:
                st.markdown("<div style='height:2.6rem'></div>", unsafe_allow_html=True)
                ai_enhance = st.checkbox("🤖 AI优化内容", value=True, help="AI帮你润色文案、添加话题标签、优化传播效果")

            submitted = st.form_submit_button("🚀 发布", type="primary", use_container_width=True)

        if submitted and content.strip():
            # AI优化
            if ai_enhance:
                with st.spinner("🤖 AI正在优化你的内容..."):
                    enhanced = _ai_enhance_post(content, post_type)
                    if enhanced:
                        content = enhanced

            type_val = {"🏆": "achievement", "📋": "case", "💬": "review", "🆘": "collab", "📢": "alert"}.get(post_type[:1], "post")
            new_post = {
                "author": f"{p['name']} @{p['institution']}",
                "avatar": "🧑‍💼",
                "time": datetime.now().strftime("%H:%M"),
                "content": content,
                "likes": 0, "comments": 0, "shares": 0,
                "type": type_val,
            }
            st.session_state.social_feed.insert(0, new_post)
            st.session_state.my_posts.insert(0, new_post)
            st.success("✅ 发布成功！你的动态已出现在社区广场。")
            st.rerun()

        # AI内容生成器
        st.markdown("---")
        st.markdown("### 🤖 AI内容生成器")
        st.caption("不知道写什么？让AI帮你生成专业的技术转移内容")

        with st.form("ai_gen_form"):
            gen_type = st.selectbox("生成类型", [
                "📊 评估报告摘要 — 把盲盒评估结果浓缩为社交动态",
                "📰 行业洞察 — 生成某个领域的最新趋势分析",
                "💡 经验分享 — 基于你的成交记录生成案例分享",
                "🆘 合作需求 — 把技术描述转化为吸引人的合作帖",
            ])
            gen_input = st.text_area("输入素材", placeholder="粘贴评估报告、技术描述、或简单描述你想分享的内容...", height=100)
            gen_submitted = st.form_submit_button("🤖 AI生成", use_container_width=True)

        if gen_submitted and gen_input.strip():
            with st.spinner("🤖 AI正在生成内容..."):
                generated = _ai_generate_post(gen_input, gen_type)
                if generated:
                    st.markdown("#### ✨ AI生成的内容")
                    st.markdown(f"<div class='card'>{generated}</div>", unsafe_allow_html=True)
                    if st.button("📋 复制并发布", type="primary"):
                        new_post = {
                            "author": f"{p['name']} @{p['institution']}",
                            "avatar": "🧑‍💼",
                            "time": datetime.now().strftime("%H:%M"),
                            "content": generated,
                            "likes": 0, "comments": 0, "shares": 0,
                            "type": "case",
                        }
                        st.session_state.social_feed.insert(0, new_post)
                        st.success("✅ 已发布！")

    # ═══════════════════════════════════════
    # Tab3: 交易管理
    # ═══════════════════════════════════════
    with tab3:
        st.markdown("### 🤝 交易管理")

        # 交易概览
        c1, c2, c3, c4 = st.columns(4)
        deals = st.session_state.deals
        with c1:
            active = sum(1 for d in deals if d["stage"] in ("matching", "negotiating"))
            st.markdown(f"""<div class="metric-box"><div class="num" style="color:#0984e3">{active}</div><div class="label">进行中</div></div>""", unsafe_allow_html=True)
        with c2:
            completed = sum(1 for d in deals if d["stage"] == "completed")
            st.markdown(f"""<div class="metric-box"><div class="num" style="color:#00b894">{completed}</div><div class="label">已成交</div></div>""", unsafe_allow_html=True)
        with c3:
            total_amount = sum(1 for d in deals if d["stage"] == "completed")
            st.markdown(f"""<div class="metric-box"><div class="num">{total_amount}</div><div class="label">累计成交(笔)</div></div>""", unsafe_allow_html=True)
        with c4:
            avg_progress = sum(d["progress"] for d in deals) // max(len(deals), 1)
            st.markdown(f"""<div class="metric-box"><div class="num">{avg_progress}%</div><div class="label">平均进度</div></div>""", unsafe_allow_html=True)

        # 新建交易
        with st.expander("➕ 发起新交易", expanded=False):
            with st.form("new_deal_form"):
                dc1, dc2 = st.columns(2)
                with dc1:
                    deal_tech = st.text_input("技术名称")
                    deal_buyer = st.text_input("买方企业")
                    deal_amount = st.text_input("预期金额", placeholder="例：200万/年")
                with dc2:
                    deal_model = st.selectbox("合作模式", ["技术许可", "排他许可", "独占许可", "技术转让", "联合开发", "技术入股"])
                    deal_source = st.selectbox("来源", ["联邦匹配", "盲盒评估", "人脉推荐", "主动对接", "其他"])
                deal_submitted = st.form_submit_button("🚀 发起交易", type="primary", use_container_width=True)

            if deal_submitted and deal_tech:
                new_deal = {
                    "id": f"D{len(deals)+1:03d}",
                    "tech": deal_tech,
                    "seller": f"{p['name']} @{p['institution']}",
                    "buyer": deal_buyer or "待定",
                    "stage": "matching",
                    "stage_label": "🔗 匹配中",
                    "amount": deal_amount or "待定",
                    "model": deal_model,
                    "created": datetime.now().strftime("%Y-%m-%d"),
                    "next_action": "发送评估报告给买方",
                    "progress": 15,
                    "timeline": [
                        {"date": datetime.now().strftime("%m-%d"), "event": f"交易发起（来源：{deal_source}）", "status": "done"},
                        {"date": "??", "event": "发送盲盒评估报告", "status": "pending"},
                        {"date": "??", "event": "买方反馈意向", "status": "pending"},
                        {"date": "??", "event": "技术交流会", "status": "pending"},
                        {"date": "??", "event": "合同签署", "status": "pending"},
                    ],
                }
                st.session_state.deals.insert(0, new_deal)
                st.success(f"✅ 交易 {new_deal['id']} 已发起！")
                st.rerun()

        # 交易列表
        st.markdown("---")
        for deal in deals:
            stage_color = {
                "matching": "#0984e3", "negotiating": "#f39c12",
                "completed": "#00b894", "failed": "#d63031",
            }.get(deal["stage"], "#636e72")

            with st.expander(f"{deal['stage_label']}  {deal['tech']}  —  {deal['buyer']}"):
                # 交易信息
                mc1, mc2, mc3, mc4 = st.columns(4)
                with mc1:
                    st.metric("合作模式", deal["model"])
                with mc2:
                    st.metric("预期金额", deal["amount"])
                with mc3:
                    st.metric("发起日期", deal["created"])
                with mc4:
                    st.metric("下一步", deal["next_action"])

                # 进度条
                st.markdown(f"""
                <div style="background:#eee;border-radius:999px;height:8px;margin:.8rem 0;overflow:hidden">
                    <div style="background:{stage_color};height:100%;width:{deal['progress']}%;border-radius:999px;transition:width .3s"></div>
                </div>
                <div style="font-size:.75rem;color:var(--muted);text-align:right">{deal['progress']}%</div>
                """, unsafe_allow_html=True)

                # 时间线
                st.markdown("#### 📅 交易时间线")
                for item in deal["timeline"]:
                    status_icon = {"done": "✅", "current": "🔵", "pending": "⬜"}.get(item["status"], "⬜")
                    status_style = "font-weight:600" if item["status"] == "current" else ""
                    st.markdown(f"`{status_icon} {item['date']}`  <span style='{status_style}'>{item['event']}</span>", unsafe_allow_html=True)

                # 操作按钮
                if deal["stage"] in ("matching", "negotiating"):
                    ac1, ac2, ac3 = st.columns(3)
                    with ac1:
                        if st.button("📤 发送评估报告", key=f"send_{deal['id']}", use_container_width=True):
                            deal["progress"] = min(deal["progress"] + 10, 100)
                            deal["next_action"] = "等待买方反馈"
                            st.success(f"✅ 评估报告已发送给 {deal['buyer']}")
                            st.rerun()
                    with ac2:
                        if st.button("💬 记录沟通", key=f"note_{deal['id']}", use_container_width=True):
                            note = st.text_input("沟通记录", key=f"note_input_{deal['id']}")
                            if note:
                                deal["timeline"].append({
                                    "date": datetime.now().strftime("%m-%d"),
                                    "event": f"沟通：{note}",
                                    "status": "done",
                                })
                                st.success("✅ 已记录")
                                st.rerun()
                    with ac3:
                        if st.button("⏭️ 推进阶段", key=f"advance_{deal['id']}", use_container_width=True):
                            if deal["stage"] == "matching":
                                deal["stage"] = "negotiating"
                                deal["stage_label"] = "🤝 谈判中"
                                deal["progress"] = min(deal["progress"] + 15, 100)
                                deal["next_action"] = "安排技术交流会"
                            elif deal["stage"] == "negotiating":
                                deal["stage"] = "completed"
                                deal["stage_label"] = "✅ 已成交"
                                deal["progress"] = 100
                                deal["next_action"] = "跟踪里程碑付款"
                            st.success("✅ 阶段已更新！")
                            st.rerun()

    # ═══════════════════════════════════════
    # Tab4: 人脉网络
    # ═══════════════════════════════════════
    with tab4:
        st.markdown("### 👥 人脉网络")

        # 网络统计
        nc1, nc2, nc3 = st.columns(3)
        with nc1:
            conn_count = len([c for c in st.session_state.connections if c["status"] == "connected"])
            st.markdown(f"""<div class="metric-box"><div class="num" style="color:#0984e3">{conn_count}</div><div class="label">已连接</div></div>""", unsafe_allow_html=True)
        with nc2:
            pending_count = len([c for c in st.session_state.connections if c["status"] == "pending"])
            st.markdown(f"""<div class="metric-box"><div class="num" style="color:#f39c12">{pending_count}</div><div class="label">待确认</div></div>""", unsafe_allow_html=True)
        with nc3:
            total_deals = sum(c.get("deals", 0) for c in st.session_state.connections)
            st.markdown(f"""<div class="metric-box"><div class="num">{total_deals}</div><div class="label">合作交易</div></div>""", unsafe_allow_html=True)

        # 推荐连接
        st.markdown("#### 🌟 推荐连接")
        st.caption("基于你的领域和交易历史，AI推荐以下OPC可能对你有帮助")

        recommendations = [
            {"name": "孙磊", "institution": "华中科技大学TTO", "field": "人工智能", "reason": "你们有3个共同关注的技术方向", "mutual": 5},
            {"name": "周婷", "institution": "南京大学双创中心", "field": "生物医药", "reason": "她正在寻找AI+医疗的合作机会", "mutual": 3},
            {"name": "吴强", "institution": "哈工大技术转移中心", "field": "先进制造", "reason": "他手头有2项技术正在寻求AI赋能", "mutual": 2},
        ]
        for rec in recommendations:
            st.markdown(f"""
            <div class="card" style="display:flex;align-items:center;gap:1rem;flex-wrap:wrap">
                <div style="font-size:2rem">🧑‍🔬</div>
                <div style="flex:1;min-width:200px">
                    <div style="font-weight:600">{rec['name']} <span style="color:var(--muted);font-weight:400;font-size:.85rem">{rec['institution']}</span></div>
                    <div style="color:var(--muted);font-size:.8rem">领域：{rec['field']} · {rec['mutual']}位共同连接</div>
                    <div style="font-size:.8rem;margin-top:.2rem">💡 {rec['reason']}</div>
                </div>
                <button style="background:#0984e3;color:#fff;border:none;padding:.4rem 1rem;border-radius:.5rem;cursor:pointer;font-size:.85rem">+ 连接</button>
            </div>""", unsafe_allow_html=True)

        # 已连接列表
        st.markdown("#### 📋 我的连接")
        for conn in st.session_state.connections:
            status_badge = "🟢 已连接" if conn["status"] == "connected" else "🟡 待确认"
            st.markdown(f"""
            <div class="card" style="display:flex;align-items:center;gap:1rem">
                <div style="font-size:1.5rem">🧑‍🔬</div>
                <div style="flex:1">
                    <span style="font-weight:600">{conn['name']}</span>
                    <span style="color:var(--muted);font-size:.85rem;margin-left:.5rem">{conn['institution']}</span>
                    <div style="color:var(--muted);font-size:.8rem">{conn['field']} · {status_badge} · {conn.get('deals',0)}次合作</div>
                </div>
                <span style="font-size:.8rem;color:var(--muted)">💬 📤 📊</span>
            </div>""", unsafe_allow_html=True)


# ─── AI辅助函数 ───
def _ai_enhance_post(content, post_type):
    """AI优化用户发布的内容"""
    system = """你是一位技术转移领域的社交媒体运营专家。优化用户发布的内容，使其更专业、更有吸引力。
规则：
1. 保持核心信息不变
2. 添加合适的emoji
3. 添加2-3个话题标签（#标签格式）
4. 优化语言表达，使其更简洁有力
5. 直接输出优化后的内容，不要解释"""
    raw = _llm_raw(system, f"请优化以下内容：\n\n{content}")
    return raw if raw else content


def _ai_generate_post(input_text, gen_type):
    """AI根据素材生成社交动态"""
    prompts = {
        "📊": "根据以下评估报告内容，生成一条适合在OPC社区发布的动态。要求：突出核心亮点、添加emoji和话题标签、语言简洁有力、200字以内。",
        "📰": "根据以下信息，生成一篇关于该领域最新趋势的分析动态。要求：有数据支撑、观点明确、添加话题标签、300字以内。",
        "💡": "根据以下成交记录，生成一条经验分享动态。要求：分享关键经验教训、对其他OPC有参考价值、添加话题标签、300字以内。",
        "🆘": "根据以下技术描述，生成一条吸引人的合作需求帖。要求：突出技术亮点和应用场景、明确合作期望、添加话题标签、200字以内。",
    }
    system = "你是一位技术转移领域的社交媒体运营专家。生成专业、有吸引力的社交动态。直接输出内容，不要解释。"
    key = gen_type[:1] if gen_type else "📊"
    prompt = prompts.get(key, prompts["📊"])
    raw = _llm_raw(system, f"{prompt}\n\n素材：\n{input_text}")
    return raw

"""创建医疗AI行业测试文档与用户 — 权限演示"""
import os, json, requests, sys

BASE = "http://localhost:8000/api"

# Login as admin
r = requests.post(f"{BASE}/auth/login", json={"username": "admin", "password": "admin123"})
if r.status_code != 200:
    print(f"Login failed: {r.status_code} {r.text}")
    sys.exit(1)
TOKEN = r.json()["access_token"]
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

docs_dir = "/tmp/med_docs"
os.makedirs(docs_dir, exist_ok=True)

# ============================================
# 医疗健康AI转型 -- 12份测试文档
# ============================================
documents = [
    # -- 公开文档 --
    {
        "filename": "01_员工手册.txt",
        "content": (
            "【员工手册 - 智慧医疗科技公司】\n\n"
            "第一章 公司简介\n智慧医疗科技致力于将AI技术应用于临床诊断、医学影像分析和药物研发。\n\n"
            "第二章 基本制度\n- 工作时间: 周一至周五 9:00-18:00\n"
            "- 考勤: 使用企业微信打卡,迟到30分钟以上记为半天事假\n\n"
            "第三章 薪酬福利\n- 基本工资+绩效奖金(季度发放)、五险一金+补充商业医疗保险\n"
            "- 每年10天带薪年假\n- 加班补偿: 工作日1.5倍、休息日2倍、法定节假日3倍\n\n"
            "第四章 信息安全\n- 严禁外传内部文档、AI训练数据必须脱敏、使用公司VPN接入"
        ),
        "visibility": "public", "department_id": None,
        "desc": "公司基本制度,全员可见",
    },
    {
        "filename": "02_AI伦理合规指南.txt",
        "content": (
            "【AI伦理与合规使用指南】\n\n"
            "1. 数据隐私保护\n- 患者数据必须脱敏: 姓名、身份证号、手机号等PII字段移除\n"
            "- 医学影像去除DICOM头中的患者信息\n\n"
            "2. 算法公平性\n- AI诊断模型须在不同性别、年龄、种族群体测试\n"
            "- 准确率差异超过5%需重训,每季度公平性审计\n\n"
            "3. 人机协作原则\n- AI诊断仅供参考,最终以医生判断为准\n"
            "- AI建议用药需药师审核,关键决策须2名以上医生签字\n\n"
            "4. 问责机制\n- AI误诊追溯: AI团队+临床团队联合评审\n- 不良事件48小时内响应"
        ),
        "visibility": "public", "department_id": None,
        "desc": "AI伦理规范,全员可见",
    },
    # -- 技术部(1) --
    {
        "filename": "03_医疗AI影像平台技术方案.md",
        "content": (
            "# 医疗AI影像诊断平台 - 技术方案\n\n"
            "## 架构\n前端(Vue3) -> API网关(FastAPI) -> 推理引擎(Triton) / 训练(GPU集群) / 存储(MinIO) -> Chroma向量库 -> DeepSeek LLM\n\n"
            "## 模型清单\n| 模型 | 用途 | 准确率 | 状态 |\n|------|------|--------|------|\n"
            "| ChestXNet v3 | 胸部X光结节检测 | 94.7% | 生产 |\n"
            "| RetinaAI | 眼底视网膜筛查 | 96.2% | 生产 |\n"
            "| PathoGPT | 病理切片判读 | 91.5% | 灰度 |\n"
            "| BoneAgeNet | 骨龄评估 | 98.1% | 生产 |\n\n"
            "## API接口\n- POST /api/v1/imaging/analyze - 提交影像分析\n"
            "- GET /api/v1/imaging/result/{task_id} - 获取结果\n"
            "- WebSocket /ws/imaging/stream - 实时流式\n\n"
            "## 性能指标\nP99延迟<500ms, 并发200QPS, GPU利用率75-85%"
        ),
        "visibility": "department", "department_id": 1,
        "desc": "技术部内部: AI影像平台架构",
    },
    {
        "filename": "04_DeepSeek模型微调指南.md",
        "content": (
            "# DeepSeek 医疗领域微调指南\n\n"
            "## 数据集\n- 医疗对话: 内部医生-患者对话(脱敏), 12万条\n"
            "- 医学文献: PubMed+中华医学期刊, 50万篇\n\n"
            "## LoRA微调参数\nr=16, alpha=32, target=q/k/v/o_proj, dropout=0.05\n\n"
            "## 评估\n| 指标 | 基座 | 微调后 | 提升 |\n"
            "|------|------|--------|------|\n| 诊断准确率 | 72.3% | 89.6% | +17.3% |\n"
            "| 用药合理性 | 68.1% | 91.2% | +23.1% |\n"
            "| 患者满意度 | 3.2/5 | 4.5/5 | +40.6% |\n\n"
            "## 注意\n禁止上传患者原始数据至DeepSeek API,微调后须通过安全审查"
        ),
        "visibility": "department", "department_id": 1,
        "desc": "技术部内部: 模型微调指南",
    },
    # -- 财务部(2) --
    {
        "filename": "05_AI项目预算与ROI分析.txt",
        "content": (
            "【AI项目预算与ROI分析 - 2026年度】\n\n"
            "一、预算分配\n| 项目 | 预算(万) | 已执行 | 执行率 |\n"
            "|------|---------|--------|--------|\n| 影像AI平台 | 800 | 520 | 65% |\n"
            "| 智能问诊 | 350 | 210 | 60% |\n| 药物研发AI | 1200 | 680 | 57% |\n"
            "| RAG知识库 | 180 | 150 | 83% |\n\n"
            "二、ROI预测\n- 影像AI: 减少医生工作量30%, 年节省240万, 回收期3.3年\n"
            "- 智能问诊: 减少导诊人员50%, 年节省120万, 回收期2.9年\n\n"
            "三、风险提示\n医保政策变动、GPU供应链波动影响"
        ),
        "visibility": "department", "department_id": 2,
        "desc": "财务部内部: AI项目预算",
    },
    {
        "filename": "06_医保结算流程优化方案.txt",
        "content": (
            "【医保结算流程AI优化方案】\n\n"
            "一、现状: 审核周期7天, 错误率3.2%\n\n"
            "二、AI优化\n1. OCR识别: PaddleOCR+医疗微调, 目标99%\n"
            "2. 规则引擎: 200+规则自动匹配+异常检测模型\n"
            "3. 智能审批: <5000元AI自动审, 5000-50000元AI初审+人工, >50000元多人会审\n\n"
            "三、效果\n审核周期1天, 错误率<0.5%, 年节省180万\n\n"
            "四、排期\nQ2 OCR上线, Q3规则引擎, Q4全量上线"
        ),
        "visibility": "department", "department_id": 2,
        "desc": "财务部内部: 医保结算优化",
    },
    # -- 人事部(3) --
    {
        "filename": "07_AI人才培养与招聘计划.txt",
        "content": (
            "【医疗AI人才培养与招聘计划 - 2026】\n\n"
            "一、招聘需求\n| 岗位 | 人数 | 年薪(万) | 紧急度 |\n"
            "|------|------|---------|--------|\n| AI算法(影像) | 3 | 40-65 | 紧急 |\n"
            "| NLP工程师(医学) | 2 | 35-55 | 紧急 |\n"
            "| 数据标注主管 | 1 | 25-35 | 高 |\n| AI产品经理(医疗) | 2 | 30-50 | 中 |\n\n"
            "二、内部培养\n- 医生AI培训: 200人, 24学时\n- 工程师医学培训: 50人, 40学时\n\n"
            "三、人才保留\n期权激励、参会资助、论文奖励(SCI一作3万)"
        ),
        "visibility": "department", "department_id": 3,
        "desc": "人事部内部: 招聘计划",
    },
    {
        "filename": "08_员工AI技能培训大纲.md",
        "content": (
            "# 员工AI技能培训大纲\n\n"
            "## 初级: AI基础(全员必修)\n- AI概论 4h, 工具使用 3h, 数据安全 2h, 伦理法规 3h\n\n"
            "## 中级: AI实践(技术岗必修)\n- Prompt工程 6h, RAG技术 8h, 模型微调 12h, 部署运维 6h\n\n"
            "## 高级: AI架构(技术Leader)\n- 系统架构 8h, 安全攻防 6h, 成本优化 4h"
        ),
        "visibility": "department", "department_id": 3,
        "desc": "人事部内部: 培训大纲",
    },
    # -- 市场部(4) --
    {
        "filename": "09_AI辅助诊断产品市场调研.txt",
        "content": (
            "【AI辅助诊断产品市场调研 - 2026Q2】\n\n"
            "一、市场规模\n| 领域 | 2025(亿) | 2026预计 | 增长率 |\n"
            "|------|---------|---------|--------|\n| 医学影像AI | 42 | 58 | 38% |\n"
            "| AI辅助诊断 | 28 | 39 | 39% |\n| AI药物研发 | 65 | 89 | 37% |\n\n"
            "二、竞品\n推想AI(肺CT,80万/年)、数坤AI(心血管,120万/年)、联影AI(一体,150万/年)\n\n"
            "三、目标客户\n三级医院3000家(IT预算500-2000万)、体检连锁(100-500万)"
        ),
        "visibility": "department", "department_id": 4,
        "desc": "市场部内部: 市场调研",
    },
    {
        "filename": "10_智慧医院品牌推广方案.txt",
        "content": (
            "【智慧医院品牌推广方案 - 2026】\n\n"
            "一、品牌定位\nAI赋能精准医疗,让每一位患者享受智慧医疗服务\n\n"
            "二、传播渠道\n| 渠道 | 形式 | 预算 |\n|------|------|------|\n"
            "| 中华放射学杂志 | 论文+广告 | 30万/年 |\n"
            "| CHIMA大会 | 展位+演讲 | 50万 |\n| RSNA | 国际展会 | 80万 |\n"
            "| 行业KOL | 测评+直播 | 40万/年 |\n\n"
            "三、案例包装\n- 协和医院: AI影像日均1200例,漏诊率降低40%\n"
            "- 瑞金医院: 冰冻切片从30分钟缩短至5分钟"
        ),
        "visibility": "department", "department_id": 4,
        "desc": "市场部内部: 品牌推广",
    },
    # -- 受限共享 --
    {
        "filename": "11_医院AI转型战略规划.txt",
        "content": (
            "【医院AI转型三年战略规划 2026-2028】\n【机密 - 共享: 技术部+市场部】\n\n"
            "2026基础建设: AI影像一期、RAG知识库、GPU集群(8*A100)\n"
            "2027推广应用: 覆盖80%科室、智能问诊日服务2000+\n"
            "2028行业领先: 区域AI中心、AI医疗器械三类证\n\n"
            "总投资: 2026年3000万 / 2027年2500万 / 2028年2000万\n\n"
            "风险: 模型泛化能力、监管不确定性、互联网巨头竞争"
        ),
        "visibility": "restricted", "department_id": None,
        "shared_dept_ids": "1,4",
        "desc": "受限: 技术部+市场部可见",
    },
    {
        "filename": "12_AI辅助诊断临床验证报告.txt",
        "content": (
            "【AI辅助诊断临床验证报告】\n【机密 - 共享: 技术部+人事部】\n\n"
            "验证机构: 协和+瑞金, 周期6个月, 样本12800例\n\n"
            "肺结节: AI敏感度96.8% vs 医生89.3%, AI+医生联合98.5%\n"
            "骨折: AI敏感度95.1% vs 医生91.5%\n脑卒中早期: AI检出87.3% vs 医生62.1%\n\n"
            "不良事件: 漏诊18例(0.14%), 误报45例(0.35%)\n\n"
            "医生满意度(120人): 诊断辅助4.6/5, 省时效果4.7/5, 总体4.5/5"
        ),
        "visibility": "restricted", "department_id": None,
        "shared_dept_ids": "1,3",
        "desc": "受限: 技术部+人事部可见",
    },
]

# Upload documents
print("=" * 70)
print("  医疗健康AI转型 - 文档权限控制演示")
print("=" * 70)

for doc in documents:
    filepath = os.path.join(docs_dir, doc["filename"])
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(doc["content"])

    form = {"visibility": doc["visibility"]}
    if doc.get("department_id"):
        form["department_id"] = str(doc["department_id"])
    if doc.get("shared_dept_ids"):
        form["shared_department_ids"] = doc["shared_dept_ids"]

    with open(filepath, "rb") as f:
        r = requests.post(
            f"{BASE}/documents/upload",
            headers=HEADERS,
            files={"file": (doc["filename"], f, "text/plain")},
            data=form,
            timeout=120,
        )

    if r.status_code == 201:
        data = r.json()
        doc["uploaded_id"] = data["id"]
        print(f"  OK [{data['id']:>2}] {doc['filename']:<40} vis={doc['visibility']:<12} | {doc['desc']}")
    else:
        print(f"  FAIL {doc['filename']}: {r.status_code} {r.text[:80]}")

# Create test users
print("\n" + "=" * 70)
print("  创建各部门测试用户")
print("=" * 70)

test_users = [
    {"username": "tech_zhang", "password": "test123", "role": "user", "department_id": 1, "label": "张工(技术部)"},
    {"username": "fin_li",     "password": "test123", "role": "user", "department_id": 2, "label": "李会计(财务部)"},
    {"username": "hr_wang",    "password": "test123", "role": "user", "department_id": 3, "label": "王经理(人事部)"},
    {"username": "mkt_chen",   "password": "test123", "role": "user", "department_id": 4, "label": "陈总监(市场部)"},
]

user_info = {}
for u in test_users:
    # Delete if exists
    r = requests.get(f"{BASE}/users/?page_size=50", headers=HEADERS)
    for existing in r.json().get("items", []):
        if existing["username"] == u["username"]:
            requests.delete(f"{BASE}/users/{existing['id']}", headers=HEADERS)

    r = requests.post(f"{BASE}/users/", headers=HEADERS, json={
        "username": u["username"],
        "password": u["password"],
        "role": u["role"],
        "department_id": u["department_id"],
    })
    if r.status_code == 201:
        r2 = requests.post(f"{BASE}/auth/login", json={"username": u["username"], "password": u["password"]})
        u["token"] = r2.json()["access_token"]
        u["user_id"] = r.json()["id"]
        user_info[u["username"]] = u
        print(f"  OK {u['username']} ({u['label']})")
    else:
        print(f"  FAIL {u['username']}: {r.status_code}")

# ============================================
# 权限验证矩阵
# ============================================
print("\n" + "=" * 70)
print("  权限验证矩阵 - 各用户可见文档")
print("=" * 70)

users_to_test = [
    ("admin", TOKEN, "管理员(admin)"),
] + [(u["username"], u["token"], u["label"]) for u in test_users]

for uname, utoken, ulabel in users_to_test:
    r = requests.get(f"{BASE}/documents/?page_size=20", headers={"Authorization": f"Bearer {utoken}"})
    if r.status_code != 200:
        print(f"\n{ulabel}: API错误 {r.status_code}")
        continue

    items = r.json()["items"]
    # Sort by id for consistent display
    items.sort(key=lambda x: x["id"])

    vis_map = {"public": "公开", "department": "部门", "restricted": "受限"}
    print(f"\n--- {ulabel} ({len(items)}份可见) ---")
    for doc in items:
        vis_cn = vis_map.get(doc["visibility"], doc["visibility"])
        print(f"  [{doc['id']:>2}] vis={vis_cn:<4} | {doc['title']}")

# Try delete as non-admin
print("\n" + "=" * 70)
print("  删除权限验证 (非管理员尝试删除)")
print("=" * 70)
tech_token = user_info["tech_zhang"]["token"]
r = requests.delete(f"{BASE}/documents/3", headers={"Authorization": f"Bearer {tech_token}"})
print(f"  tech_zhang DELETE doc#3: {r.status_code} (403=正确拒绝)")

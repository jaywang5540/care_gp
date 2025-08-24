# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

Medicare GP Assistant (Care GP) - AI辅助Medicare Benefits Schedule账单系统

这是一个基于FastAPI的轻量级系统，帮助澳大利亚全科医生通过AI辅助处理诊疗内容来自动化Medicare账单。系统根据诊疗内容推荐合适的MBS（Medicare Benefits Schedule）项目编码，并生成符合规范的账单文档。

## 开发命令

### 安装和运行
```bash
# 安装依赖
pip install -r requirements.txt

# 运行开发服务器（带热重载）
python run.py

# 自定义参数运行
python run.py --host 0.0.0.0 --port 8000 --reload
```

### 访问地址
- Web界面: http://localhost:8000
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/api/v1/health

## 系统架构

### 核心设计原则
- **无需数据库**: 所有数据以JSON文件形式存储在 `data/` 目录
- **无需认证**: 简化系统，专注于Medicare核心功能
- **最小依赖**: 只包含必要的包（FastAPI、Pydantic、Loguru）

### 数据存储结构
```
data/
├── mbs_codes/          # MBS项目编码数据库（首次运行时自动创建）
│   └── mbs_items.json  # 包含Medicare账单编码和规则
├── consultations/      # 诊疗记录按日期组织
│   └── YYYY-MM-DD/     # 每日文件夹包含诊疗JSON文件
└── documents/          # 生成的文档
    ├── claims/         # Medicare账单文档
    ├── summaries/      # 诊疗摘要
    ├── referrals/      # 转诊信
    └── care_plans/     # 护理计划
```

### 服务层架构

应用采用三层架构：

1. **API层** (`app/api/v1/endpoints/`)
   - `medicare.py`: MBS推荐、账单生成、合规检查
   - `consultation.py`: 诊疗处理和文档生成
   - `health.py`: 系统健康监控

2. **服务层** (`app/services/`)
   - `MBSService`: 管理MBS项目数据和推荐逻辑
     - 首次运行时自动创建示例MBS数据
     - 基于诊疗时长和内容推荐项目
   - `TextProcessor`: 从诊疗文本中提取临床信息
     - 识别症状、诊断、治疗方案
     - 检测患者年龄、紧急程度、慢性病
   - `DocumentGenerator`: 创建符合Medicare规范的文档
     - 生成账单、摘要、转诊信、护理计划

3. **数据模型层** (`app/schemas/`)
   - Pydantic模型用于请求/响应验证
   - 确保整个应用的数据一致性

### MBS推荐逻辑

系统使用智能匹配，基于以下因素：
- **诊疗时长**: 映射到MBS Level A/B/C/D项目
  - < 6分钟 → Level A (项目3)
  - 6-20分钟 → Level B (项目23)
  - 20-40分钟 → Level C (项目36)
  - > 40分钟 → Level D (项目44)
- **患者年龄**: 75岁以上触发健康评估推荐（项目703）
- **内容分析**: 检测心理健康（721/723）、慢性病（732）、紧急护理（10997）
- **合规规则**: 验证项目组合和时间要求

### 主要API端点

```
POST /api/v1/medicare/recommend
  - 输入: 诊疗文本、时长、患者年龄
  - 输出: 排序的MBS推荐及置信度分数

POST /api/v1/medicare/generate-claim
  - 输入: MBS项目、患者/医生详情
  - 输出: Medicare账单文档和数据

POST /api/v1/medicare/check-compliance
  - 输入: MBS项目组合
  - 输出: 合规状态、警告、建议

POST /api/v1/consultation/process
  - 输入: 诊疗文本/语音
  - 输出: 提取的信息、MBS推荐、文档路径
```

### 配置说明

`.env` 环境变量：
- `APP_NAME`: 应用名称
- `LOG_LEVEL`: 日志级别（INFO/DEBUG/ERROR）
- `DATA_PATH`: 数据存储基础路径
- `PORT`: 服务器端口（默认: 8000）

### 测试界面

Web界面（`static/index.html`）包含：
- **测试数据生成器**: 创建真实的诊疗场景
  - 8个预配置的诊疗模板
  - 随机患者/医生信息
  - 智能MBS项目预选
- **实时API测试**: 直接与所有端点交互
- **可视化反馈**: 颜色编码的置信度和合规状态

## 重要实现细节

### 示例MBS数据
首次运行时，`MBSService._create_sample_mbs_data()` 创建10个常用GP账单项目，包括标准诊疗（3、23、36、44）、心理健康计划（721、723）、健康评估（701、703）、慢性病管理（732）和下班后护理（10997）。

### 文本处理关键词
`TextProcessor` 使用关键词字典：
- **症状**: pain、fever、cough、headache、fatigue、nausea、anxiety、depression
- **诊断**: respiratory、cardiovascular、diabetes、mental_health
- **治疗**: medication、referral、test、counselling

### 文档生成
所有文档同时生成JSON（用于数据）和TXT（用于阅读）格式，使用时间戳和唯一ID存储以便追踪。

### 错误处理
- 请求ID贯穿整个请求生命周期
- 所有错误记录到 `logs/error_YYYY-MM-DD.log`
- 错误消息包含详细信息便于调试

## 测试数据场景

系统包含8种预定义的诊疗场景：
1. **标准诊疗**: 头痛、运动损伤、呼吸道感染
2. **心理健康评估**: 焦虑抑郁、治疗计划制定
3. **慢性病管理**: 糖尿病复查、高血压管理
4. **老年健康评估**: 75岁以上年度体检
5. **紧急诊疗**: 胸痛、紧急转诊

每个场景都有对应的MBS项目推荐逻辑，确保账单的准确性和合规性。
from typing import List, Dict, Any, Optional
from app.schemas.medicare import MBSItem, MBSRecommendation
from app.core.config import settings
from app.core.logger import logger
import json
from pathlib import Path

class MBSService:
    """MBS项目服务类"""
    
    def __init__(self):
        self.mbs_data = self._load_mbs_data()
    
    def _load_mbs_data(self) -> List[Dict[str, Any]]:
        """加载MBS数据"""
        mbs_file = settings.MBS_DATA_PATH / "mbs_items.json"
        
        # 如果文件不存在，创建示例数据
        if not mbs_file.exists():
            logger.info("MBS数据文件不存在，创建示例数据")
            self._create_sample_mbs_data(mbs_file)
        
        try:
            with open(mbs_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"加载了 {len(data)} 个MBS项目")
                return data
        except Exception as e:
            logger.error(f"加载MBS数据失败: {e}")
            return []
    
    def _create_sample_mbs_data(self, file_path: Path):
        """创建示例MBS数据"""
        sample_data = [
            {
                "item_number": "3",
                "description": "Level A consultation - brief",
                "category": "A1",
                "fee": 18.95,
                "schedule_fee": 18.95,
                "benefit": 100,
                "duration": "< 6 minutes",
                "requirements": ["Brief consultation", "Straightforward clinical problem"]
            },
            {
                "item_number": "23",
                "description": "Level B consultation - standard",
                "category": "A1",
                "fee": 40.85,
                "schedule_fee": 40.85,
                "benefit": 100,
                "duration": "6-20 minutes",
                "requirements": ["Standard consultation", "Taking history", "Clinical examination", "Management plan"]
            },
            {
                "item_number": "36",
                "description": "Level C consultation - long",
                "category": "A1",
                "fee": 76.95,
                "schedule_fee": 76.95,
                "benefit": 100,
                "duration": "20-40 minutes",
                "requirements": ["Detailed history", "Comprehensive examination", "Complex problem"]
            },
            {
                "item_number": "44",
                "description": "Level D consultation - prolonged",
                "category": "A1",
                "fee": 113.30,
                "schedule_fee": 113.30,
                "benefit": 100,
                "duration": "> 40 minutes",
                "requirements": ["Extended consultation", "Complex medical problem", "Detailed counselling"]
            },
            {
                "item_number": "721",
                "description": "GP Mental Health Treatment Plan",
                "category": "A20",
                "fee": 96.65,
                "schedule_fee": 96.65,
                "benefit": 100,
                "duration": "> 20 minutes",
                "requirements": ["Mental health assessment", "Treatment plan development", "Referral arrangements"]
            },
            {
                "item_number": "723",
                "description": "GP Mental Health Treatment Plan Review",
                "category": "A20",
                "fee": 75.05,
                "schedule_fee": 75.05,
                "benefit": 100,
                "duration": "> 20 minutes",
                "requirements": ["Review of mental health treatment plan", "Progress assessment"]
            },
            {
                "item_number": "703",
                "description": "Health assessment for person aged 75 years and older",
                "category": "A14",
                "fee": 144.80,
                "schedule_fee": 144.80,
                "benefit": 100,
                "duration": "> 30 minutes",
                "requirements": ["Comprehensive health assessment", "Age 75+", "Annual assessment"]
            },
            {
                "item_number": "701",
                "description": "Brief health assessment",
                "category": "A14",
                "fee": 63.75,
                "schedule_fee": 63.75,
                "benefit": 100,
                "duration": "< 30 minutes",
                "requirements": ["Health assessment", "Specific patient groups"]
            },
            {
                "item_number": "732",
                "description": "GP Management Plan (GPMP)",
                "category": "A15",
                "fee": 150.35,
                "schedule_fee": 150.35,
                "benefit": 100,
                "duration": "> 20 minutes",
                "requirements": ["Chronic disease", "Comprehensive management plan", "Multidisciplinary care"]
            },
            {
                "item_number": "10997",
                "description": "After hours consultation - urgent",
                "category": "A11",
                "fee": 137.95,
                "schedule_fee": 137.95,
                "benefit": 100,
                "duration": "Variable",
                "requirements": ["After hours service", "Urgent medical condition", "Outside normal hours"]
            }
        ]
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"创建了 {len(sample_data)} 个示例MBS项目")
    
    def get_mbs_items(self, category: str = None, search: str = None) -> List[Dict[str, Any]]:
        """获取MBS项目列表"""
        items = self.mbs_data
        
        # 按类别筛选
        if category:
            items = [item for item in items if item.get("category") == category]
        
        # 搜索
        if search:
            search_lower = search.lower()
            items = [
                item for item in items
                if search_lower in item.get("description", "").lower()
                or search_lower in item.get("item_number", "").lower()
            ]
        
        return items
    
    def get_mbs_item(self, item_number: str) -> Optional[Dict[str, Any]]:
        """根据项目编号获取MBS项目"""
        for item in self.mbs_data:
            if item.get("item_number") == item_number:
                return item
        return None
    
    def recommend_mbs_items(self, consultation_info: Dict[str, Any]) -> List[MBSRecommendation]:
        """根据诊疗信息推荐MBS项目"""
        recommendations = []
        
        # 获取诊疗时长
        duration = consultation_info.get("consultation_duration", consultation_info.get("duration_minutes", 15))
        
        # 基于时长推荐标准诊疗项目
        if duration < 6:
            item = self.get_mbs_item("3")
            if item:
                recommendations.append(MBSRecommendation(
                    item_number="3",
                    description=item["description"],
                    confidence=0.9,
                    reason=f"诊疗时长{duration}分钟，适合Level A简短诊疗",
                    compliance_notes=["确保诊疗内容符合简短诊疗要求"]
                ))
        elif duration <= 20:
            item = self.get_mbs_item("23")
            if item:
                recommendations.append(MBSRecommendation(
                    item_number="23",
                    description=item["description"],
                    confidence=0.95,
                    reason=f"诊疗时长{duration}分钟，适合Level B标准诊疗",
                    compliance_notes=["最常用的GP诊疗项目"]
                ))
        elif duration <= 40:
            item = self.get_mbs_item("36")
            if item:
                recommendations.append(MBSRecommendation(
                    item_number="36",
                    description=item["description"],
                    confidence=0.9,
                    reason=f"诊疗时长{duration}分钟，适合Level C长时诊疗",
                    compliance_notes=["需要详细病史和全面检查"]
                ))
        else:
            item = self.get_mbs_item("44")
            if item:
                recommendations.append(MBSRecommendation(
                    item_number="44",
                    description=item["description"],
                    confidence=0.85,
                    reason=f"诊疗时长{duration}分钟，适合Level D延长诊疗",
                    compliance_notes=["复杂医疗问题，需要详细咨询"]
                ))
        
        # 检查是否涉及心理健康
        text = str(consultation_info.get("raw_text", "")).lower()
        if any(keyword in text for keyword in ["mental", "depression", "anxiety", "心理", "抑郁", "焦虑"]):
            item = self.get_mbs_item("721")
            if item:
                recommendations.append(MBSRecommendation(
                    item_number="721",
                    description=item["description"],
                    confidence=0.8,
                    reason="检测到心理健康相关内容，可能需要心理健康治疗计划",
                    compliance_notes=["需要完成心理健康评估", "制定治疗计划"]
                ))
        
        # 检查患者年龄
        age = consultation_info.get("patient_age")
        if age and age >= 75:
            item = self.get_mbs_item("703")
            if item:
                recommendations.append(MBSRecommendation(
                    item_number="703",
                    description=item["description"],
                    confidence=0.7,
                    reason=f"患者年龄{age}岁，符合75岁以上健康评估条件",
                    compliance_notes=["年度健康评估", "需要全面健康检查"]
                ))
        
        # 检查是否提到慢性病管理
        if any(keyword in text for keyword in ["chronic", "diabetes", "hypertension", "慢性", "糖尿病", "高血压"]):
            item = self.get_mbs_item("732")
            if item:
                recommendations.append(MBSRecommendation(
                    item_number="732",
                    description=item["description"],
                    confidence=0.75,
                    reason="检测到慢性病相关内容，可能需要GP管理计划",
                    compliance_notes=["慢性病管理", "需要制定综合管理计划"]
                ))
        
        # 按置信度排序
        recommendations.sort(key=lambda x: x.confidence, reverse=True)
        
        # 返回前5个推荐
        return recommendations[:5]
    
    def check_compliance(
        self,
        mbs_items: List[str],
        patient_history: Optional[Dict[str, Any]] = None,
        consultation_details: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """检查MBS项目合规性"""
        result = {
            "is_compliant": True,
            "warnings": [],
            "errors": [],
            "suggestions": [],
            "details": {}
        }
        
        # 检查项目组合
        if len(mbs_items) > 1:
            # 检查是否有互斥项目
            consultation_items = ["3", "23", "36", "44"]
            consultation_count = sum(1 for item in mbs_items if item in consultation_items)
            if consultation_count > 1:
                result["errors"].append("同一次诊疗不能同时收取多个标准诊疗费用")
                result["is_compliant"] = False
        
        # 检查时间限制
        for item_number in mbs_items:
            item = self.get_mbs_item(item_number)
            if not item:
                result["warnings"].append(f"MBS项目 {item_number} 不存在")
                continue
            
            # 检查时长要求
            if "duration" in item:
                required_duration = item.get("duration", "")
                actual_duration = consultation_details.get("duration_minutes", 0)
                
                if "< 6" in required_duration and actual_duration >= 6:
                    result["warnings"].append(f"项目{item_number}要求诊疗时长少于6分钟")
                elif "6-20" in required_duration and (actual_duration < 6 or actual_duration > 20):
                    result["warnings"].append(f"项目{item_number}要求诊疗时长6-20分钟")
                elif "20-40" in required_duration and (actual_duration < 20 or actual_duration > 40):
                    result["warnings"].append(f"项目{item_number}要求诊疗时长20-40分钟")
                elif "> 40" in required_duration and actual_duration <= 40:
                    result["warnings"].append(f"项目{item_number}要求诊疗时长超过40分钟")
        
        # 检查患者历史
        if patient_history:
            # 检查是否有重复收费
            recent_claims = patient_history.get("recent_claims", [])
            for item_number in mbs_items:
                if item_number in recent_claims:
                    result["warnings"].append(f"项目{item_number}最近已经收取过，请确认是否符合时间间隔要求")
        
        # 提供建议
        if not result["errors"] and not result["warnings"]:
            result["suggestions"].append("所有项目符合基本合规要求")
        else:
            result["suggestions"].append("请仔细核对项目要求，确保符合Medicare规定")
        
        # 更新合规状态
        if result["errors"]:
            result["is_compliant"] = False
        
        return result
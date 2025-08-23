from typing import Dict, Any, List, Optional
from app.core.logger import logger
import re
from datetime import datetime

class TextProcessor:
    """文本处理服务类"""
    
    def __init__(self):
        # 症状关键词
        self.symptom_keywords = {
            "pain": ["pain", "ache", "hurt", "sore", "疼", "痛"],
            "fever": ["fever", "temperature", "热", "发烧", "发热"],
            "cough": ["cough", "咳", "咳嗽"],
            "headache": ["headache", "头痛", "头疼"],
            "fatigue": ["tired", "fatigue", "exhausted", "疲劳", "累", "乏力"],
            "nausea": ["nausea", "vomit", "恶心", "呕吐"],
            "anxiety": ["anxiety", "anxious", "worried", "焦虑", "担心"],
            "depression": ["depression", "depressed", "sad", "抑郁", "沮丧"]
        }
        
        # 诊断关键词
        self.diagnosis_keywords = {
            "respiratory": ["respiratory", "bronchitis", "pneumonia", "呼吸", "肺炎", "支气管"],
            "cardiovascular": ["heart", "cardiac", "hypertension", "心脏", "高血压", "心血管"],
            "diabetes": ["diabetes", "blood sugar", "glucose", "糖尿病", "血糖"],
            "mental_health": ["mental", "psychiatric", "depression", "anxiety", "心理", "精神", "抑郁", "焦虑"]
        }
        
        # 治疗关键词
        self.treatment_keywords = {
            "medication": ["prescribe", "medication", "drug", "开药", "处方", "药物"],
            "referral": ["refer", "specialist", "转诊", "专科"],
            "test": ["test", "examination", "x-ray", "blood test", "检查", "化验", "X光"],
            "counselling": ["counsel", "therapy", "咨询", "治疗"]
        }
    
    def extract_consultation_info(self, text: str) -> Dict[str, Any]:
        """
        从诊疗文本中提取关键信息
        
        Args:
            text: 诊疗对话文本
            
        Returns:
            提取的信息字典
        """
        logger.info("开始提取诊疗信息")
        
        extracted_info = {
            "raw_text": text,
            "symptoms": [],
            "diagnoses": [],
            "treatments": [],
            "duration_mentioned": None,
            "patient_age_mentioned": None,
            "urgency_level": "routine",
            "key_phrases": [],
            "extracted_at": datetime.now().isoformat()
        }
        
        # 转换为小写以便匹配
        text_lower = text.lower()
        
        # 提取症状
        for symptom_type, keywords in self.symptom_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                extracted_info["symptoms"].append(symptom_type)
        
        # 提取可能的诊断
        for diagnosis_type, keywords in self.diagnosis_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                extracted_info["diagnoses"].append(diagnosis_type)
        
        # 提取治疗方式
        for treatment_type, keywords in self.treatment_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                extracted_info["treatments"].append(treatment_type)
        
        # 提取时长信息
        duration_patterns = [
            r'(\d+)\s*(?:minutes?|mins?|分钟?)',
            r'(\d+)\s*(?:hours?|hrs?|小时?)',
        ]
        for pattern in duration_patterns:
            match = re.search(pattern, text_lower)
            if match:
                duration = int(match.group(1))
                if "hour" in pattern or "小时" in pattern:
                    duration *= 60  # 转换为分钟
                extracted_info["duration_mentioned"] = duration
                break
        
        # 提取年龄信息
        age_patterns = [
            r'(\d+)\s*(?:years?\s*old|岁)',
            r'age[d]?\s*(\d+)',
            r'患者.*?(\d+)岁',
        ]
        for pattern in age_patterns:
            match = re.search(pattern, text_lower)
            if match:
                extracted_info["patient_age_mentioned"] = int(match.group(1))
                break
        
        # 判断紧急程度
        urgent_keywords = ["urgent", "emergency", "severe", "acute", "紧急", "严重", "急性"]
        if any(keyword in text_lower for keyword in urgent_keywords):
            extracted_info["urgency_level"] = "urgent"
        
        # 提取关键短语（前50个字符的句子）
        sentences = re.split(r'[.!?。！？]', text)
        key_phrases = [s.strip() for s in sentences if len(s.strip()) > 10][:3]
        extracted_info["key_phrases"] = key_phrases
        
        # 检测是否涉及慢性病
        chronic_keywords = ["chronic", "long-term", "ongoing", "慢性", "长期"]
        if any(keyword in text_lower for keyword in chronic_keywords):
            extracted_info["is_chronic"] = True
        else:
            extracted_info["is_chronic"] = False
        
        # 检测是否需要随访
        followup_keywords = ["follow up", "review", "return", "复诊", "随访", "复查"]
        if any(keyword in text_lower for keyword in followup_keywords):
            extracted_info["needs_followup"] = True
        else:
            extracted_info["needs_followup"] = False
        
        logger.info(f"提取完成: 症状{len(extracted_info['symptoms'])}个, "
                   f"诊断{len(extracted_info['diagnoses'])}个, "
                   f"治疗{len(extracted_info['treatments'])}个")
        
        return extracted_info
    
    def extract_patient_info(self, text: str) -> Dict[str, Any]:
        """
        从文本中提取患者信息
        
        Args:
            text: 包含患者信息的文本
            
        Returns:
            患者信息字典
        """
        patient_info = {
            "name": None,
            "age": None,
            "gender": None,
            "medicare_number": None,
            "contact": None
        }
        
        text_lower = text.lower()
        
        # 提取姓名（简单模式匹配）
        name_patterns = [
            r'(?:patient|name|患者|姓名)[:\s]*([A-Za-z\s]+)',
            r'(?:mr|mrs|ms|miss|dr)\.?\s+([A-Za-z\s]+)',
        ]
        for pattern in name_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                patient_info["name"] = match.group(1).strip()
                break
        
        # 提取年龄
        age_match = re.search(r'(\d+)\s*(?:years?\s*old|岁|y/?o)', text_lower)
        if age_match:
            patient_info["age"] = int(age_match.group(1))
        
        # 提取性别
        if any(word in text_lower for word in ["male", "man", "男", "先生"]):
            patient_info["gender"] = "male"
        elif any(word in text_lower for word in ["female", "woman", "女", "女士"]):
            patient_info["gender"] = "female"
        
        # 提取Medicare号码（10位数字）
        medicare_match = re.search(r'\b(\d{10})\b', text)
        if medicare_match:
            patient_info["medicare_number"] = medicare_match.group(1)
        
        # 提取联系方式（电话号码）
        phone_match = re.search(r'(?:0|\+61)\d{9,10}', text)
        if phone_match:
            patient_info["contact"] = phone_match.group(0)
        
        return patient_info
    
    def summarize_consultation(self, consultation_data: Dict[str, Any]) -> str:
        """
        生成诊疗摘要
        
        Args:
            consultation_data: 诊疗数据
            
        Returns:
            摘要文本
        """
        summary_parts = []
        
        # 添加基本信息
        if consultation_data.get("consultation_date"):
            summary_parts.append(f"Date: {consultation_data['consultation_date']}")
        
        if consultation_data.get("patient_id"):
            summary_parts.append(f"Patient ID: {consultation_data['patient_id']}")
        
        # 添加症状
        symptoms = consultation_data.get("extracted_info", {}).get("symptoms", [])
        if symptoms:
            summary_parts.append(f"Presenting symptoms: {', '.join(symptoms)}")
        
        # 添加诊断
        diagnoses = consultation_data.get("extracted_info", {}).get("diagnoses", [])
        if diagnoses:
            summary_parts.append(f"Possible diagnoses: {', '.join(diagnoses)}")
        
        # 添加治疗
        treatments = consultation_data.get("extracted_info", {}).get("treatments", [])
        if treatments:
            summary_parts.append(f"Treatment approach: {', '.join(treatments)}")
        
        # 添加MBS推荐
        mbs_items = consultation_data.get("mbs_recommendations", [])
        if mbs_items:
            mbs_numbers = [item.get("item_number", "") for item in mbs_items[:3]]
            summary_parts.append(f"Recommended MBS items: {', '.join(mbs_numbers)}")
        
        # 添加随访信息
        if consultation_data.get("extracted_info", {}).get("needs_followup"):
            summary_parts.append("Follow-up required")
        
        return "\n".join(summary_parts)
    
    def validate_text_input(self, text: str) -> Dict[str, Any]:
        """
        验证文本输入
        
        Args:
            text: 输入文本
            
        Returns:
            验证结果
        """
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "text_length": len(text),
            "word_count": len(text.split())
        }
        
        # 检查文本长度
        if len(text) < 10:
            validation_result["errors"].append("文本太短，至少需要10个字符")
            validation_result["is_valid"] = False
        elif len(text) > 10000:
            validation_result["warnings"].append("文本过长，可能影响处理速度")
        
        # 检查是否包含有效内容
        if not re.search(r'[a-zA-Z\u4e00-\u9fa5]+', text):
            validation_result["errors"].append("文本不包含有效内容")
            validation_result["is_valid"] = False
        
        # 检查是否包含敏感信息（简单检查）
        sensitive_patterns = [
            r'\b\d{9,}\b',  # 长数字串（可能是ID或电话）
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
        ]
        for pattern in sensitive_patterns:
            if re.search(pattern, text):
                validation_result["warnings"].append("文本可能包含敏感信息，请注意隐私保护")
                break
        
        return validation_result
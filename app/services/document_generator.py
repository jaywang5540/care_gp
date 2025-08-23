from typing import Dict, Any, Optional
from app.core.config import settings
from app.core.logger import logger
from datetime import datetime
import json
from pathlib import Path

class DocumentGenerator:
    """文档生成服务类"""
    
    def __init__(self):
        self.documents_path = settings.DOCUMENTS_PATH
    
    def generate_claim_document(self, claim_id: str, claim_data: Dict[str, Any]) -> str:
        """
        生成Medicare账单文档
        
        Args:
            claim_id: 账单ID
            claim_data: 账单数据
            
        Returns:
            文档路径
        """
        logger.info(f"生成账单文档: {claim_id}")
        
        # 创建日期目录
        date_str = datetime.now().strftime("%Y-%m-%d")
        date_path = self.documents_path / "claims" / date_str
        date_path.mkdir(parents=True, exist_ok=True)
        
        # 生成文档内容
        document_content = self._format_claim_document(claim_data)
        
        # 保存为JSON和文本格式
        json_path = date_path / f"{claim_id}.json"
        txt_path = date_path / f"{claim_id}.txt"
        
        # 保存JSON
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(claim_data, f, ensure_ascii=False, indent=2)
        
        # 保存文本
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(document_content)
        
        logger.info(f"账单文档已保存: {txt_path}")
        return str(txt_path)
    
    def _format_claim_document(self, claim_data: Dict[str, Any]) -> str:
        """格式化账单文档"""
        lines = [
            "=" * 60,
            "MEDICARE BENEFITS SCHEDULE CLAIM",
            "=" * 60,
            "",
            f"Claim ID: {claim_data.get('claim_id', 'N/A')}",
            f"Claim Date: {claim_data.get('claim_date', 'N/A')}",
            "",
            "PROVIDER DETAILS:",
            "-" * 40,
        ]
        
        provider = claim_data.get('provider', {})
        lines.extend([
            f"Provider Number: {provider.get('provider_number', 'N/A')}",
            f"Provider Name: {provider.get('name', 'N/A')}",
            "",
            "PATIENT DETAILS:",
            "-" * 40,
        ])
        
        patient = claim_data.get('patient', {})
        lines.extend([
            f"Medicare Number: {patient.get('medicare_number', 'N/A')}",
            f"Patient Name: {patient.get('name', 'N/A')}",
            f"Date of Birth: {patient.get('dob', 'N/A')}",
            "",
            "SERVICE DETAILS:",
            "-" * 40,
            f"Consultation Date: {claim_data.get('consultation_date', 'N/A')}",
            "",
            "MBS ITEMS:",
            "-" * 40,
        ])
        
        # 添加项目明细
        items = claim_data.get('items', [])
        for item in items:
            lines.extend([
                f"Item Number: {item.get('item_number', 'N/A')}",
                f"Description: {item.get('description', 'N/A')}",
                f"Fee: ${item.get('fee', 0):.2f}",
                f"Benefit: ${item.get('benefit', 0):.2f}",
                ""
            ])
        
        lines.extend([
            "=" * 60,
            f"TOTAL FEE: ${claim_data.get('total_fee', 0):.2f}",
            f"TOTAL BENEFIT: ${claim_data.get('total_benefit', 0):.2f}",
            "=" * 60,
            "",
            "This document is generated automatically.",
            f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ])
        
        return "\n".join(lines)
    
    def generate_consultation_summary(self, consultation_id: str, consultation_data: Dict[str, Any]) -> str:
        """
        生成诊疗摘要文档
        
        Args:
            consultation_id: 诊疗ID
            consultation_data: 诊疗数据
            
        Returns:
            文档路径
        """
        logger.info(f"生成诊疗摘要: {consultation_id}")
        
        # 创建日期目录
        date_str = datetime.now().strftime("%Y-%m-%d")
        date_path = self.documents_path / "summaries" / date_str
        date_path.mkdir(parents=True, exist_ok=True)
        
        # 生成摘要内容
        summary_content = self._format_consultation_summary(consultation_data)
        
        # 保存文档
        file_path = date_path / f"{consultation_id}_summary.txt"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        logger.info(f"诊疗摘要已保存: {file_path}")
        return str(file_path)
    
    def _format_consultation_summary(self, data: Dict[str, Any]) -> str:
        """格式化诊疗摘要"""
        lines = [
            "=" * 60,
            "CONSULTATION SUMMARY",
            "=" * 60,
            "",
            f"Consultation ID: {data.get('consultation_id', 'N/A')}",
            f"Date: {data.get('consultation_date', 'N/A')}",
            f"Duration: {data.get('duration_minutes', 'N/A')} minutes",
            "",
            "PATIENT INFORMATION:",
            "-" * 40,
            f"Patient ID: {data.get('patient_id', 'N/A')}",
            f"Provider ID: {data.get('provider_id', 'N/A')}",
            ""
        ]
        
        # 添加提取的信息
        extracted = data.get('extracted_info', {})
        if extracted:
            lines.extend([
                "CLINICAL INFORMATION:",
                "-" * 40,
            ])
            
            if extracted.get('symptoms'):
                lines.append(f"Symptoms: {', '.join(extracted['symptoms'])}")
            
            if extracted.get('diagnoses'):
                lines.append(f"Possible Diagnoses: {', '.join(extracted['diagnoses'])}")
            
            if extracted.get('treatments'):
                lines.append(f"Treatments: {', '.join(extracted['treatments'])}")
            
            if extracted.get('urgency_level'):
                lines.append(f"Urgency Level: {extracted['urgency_level']}")
            
            lines.append("")
        
        # 添加MBS推荐
        mbs_items = data.get('mbs_recommendations', [])
        if mbs_items:
            lines.extend([
                "RECOMMENDED MBS ITEMS:",
                "-" * 40,
            ])
            
            for item in mbs_items:
                lines.extend([
                    f"• Item {item.get('item_number', 'N/A')}: {item.get('description', 'N/A')}",
                    f"  Confidence: {item.get('confidence', 0):.1%}",
                    f"  Reason: {item.get('reason', 'N/A')}",
                ])
            
            lines.append("")
        
        # 添加原始输入（前200字符）
        if data.get('raw_input'):
            raw_text = data['raw_input'][:200]
            if len(data['raw_input']) > 200:
                raw_text += "..."
            
            lines.extend([
                "CONSULTATION NOTES (excerpt):",
                "-" * 40,
                raw_text,
                ""
            ])
        
        lines.extend([
            "=" * 60,
            f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ])
        
        return "\n".join(lines)
    
    def generate_referral_letter(self, consultation_id: str, consultation_data: Dict[str, Any]) -> str:
        """
        生成转诊信
        
        Args:
            consultation_id: 诊疗ID
            consultation_data: 诊疗数据
            
        Returns:
            文档路径
        """
        logger.info(f"生成转诊信: {consultation_id}")
        
        # 创建日期目录
        date_str = datetime.now().strftime("%Y-%m-%d")
        date_path = self.documents_path / "referrals" / date_str
        date_path.mkdir(parents=True, exist_ok=True)
        
        # 生成转诊信内容
        letter_content = self._format_referral_letter(consultation_data)
        
        # 保存文档
        file_path = date_path / f"{consultation_id}_referral.txt"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(letter_content)
        
        logger.info(f"转诊信已保存: {file_path}")
        return str(file_path)
    
    def _format_referral_letter(self, data: Dict[str, Any]) -> str:
        """格式化转诊信"""
        date_str = datetime.now().strftime("%B %d, %Y")
        
        lines = [
            "REFERRAL LETTER",
            "=" * 60,
            "",
            date_str,
            "",
            "Dear Specialist,",
            "",
            f"Re: Patient ID {data.get('patient_id', 'N/A')}",
            "",
            "I am referring this patient to you for further assessment and management.",
            "",
            "CLINICAL SUMMARY:",
            "-" * 40,
        ]
        
        # 添加临床信息
        extracted = data.get('extracted_info', {})
        
        if extracted.get('symptoms'):
            lines.append(f"Presenting Symptoms: {', '.join(extracted['symptoms'])}")
        
        if extracted.get('diagnoses'):
            lines.append(f"Provisional Diagnosis: {', '.join(extracted['diagnoses'])}")
        
        if extracted.get('treatments'):
            lines.append(f"Current Management: {', '.join(extracted['treatments'])}")
        
        lines.extend([
            "",
            "REASON FOR REFERRAL:",
            "-" * 40,
            "The patient requires specialist assessment for further evaluation and management.",
            "",
            "Thank you for seeing this patient. I look forward to your assessment and recommendations.",
            "",
            "Yours sincerely,",
            "",
            "",
            f"Dr. {data.get('provider_id', 'Provider')}",
            "General Practitioner",
            "",
            "=" * 60,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ])
        
        return "\n".join(lines)
    
    def generate_care_plan(self, consultation_id: str, consultation_data: Dict[str, Any]) -> str:
        """
        生成护理计划
        
        Args:
            consultation_id: 诊疗ID
            consultation_data: 诊疗数据
            
        Returns:
            文档路径
        """
        logger.info(f"生成护理计划: {consultation_id}")
        
        # 创建日期目录
        date_str = datetime.now().strftime("%Y-%m-%d")
        date_path = self.documents_path / "care_plans" / date_str
        date_path.mkdir(parents=True, exist_ok=True)
        
        # 生成护理计划内容
        plan_content = self._format_care_plan(consultation_data)
        
        # 保存文档
        file_path = date_path / f"{consultation_id}_care_plan.txt"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(plan_content)
        
        logger.info(f"护理计划已保存: {file_path}")
        return str(file_path)
    
    def _format_care_plan(self, data: Dict[str, Any]) -> str:
        """格式化护理计划"""
        lines = [
            "CARE PLAN",
            "=" * 60,
            "",
            f"Patient ID: {data.get('patient_id', 'N/A')}",
            f"Date: {datetime.now().strftime('%Y-%m-%d')}",
            f"Provider: {data.get('provider_id', 'N/A')}",
            "",
            "HEALTH CONDITIONS:",
            "-" * 40,
        ]
        
        # 添加健康状况
        extracted = data.get('extracted_info', {})
        
        if extracted.get('diagnoses'):
            for diagnosis in extracted['diagnoses']:
                lines.append(f"• {diagnosis}")
        else:
            lines.append("• To be assessed")
        
        lines.extend([
            "",
            "CARE OBJECTIVES:",
            "-" * 40,
            "• Improve patient health outcomes",
            "• Coordinate multidisciplinary care",
            "• Monitor progress and adjust treatment",
            "",
            "PLANNED INTERVENTIONS:",
            "-" * 40,
        ])
        
        # 添加计划的干预措施
        if extracted.get('treatments'):
            for treatment in extracted['treatments']:
                lines.append(f"• {treatment}")
        else:
            lines.extend([
                "• Regular monitoring",
                "• Medication management",
                "• Lifestyle modifications"
            ])
        
        lines.extend([
            "",
            "FOLLOW-UP SCHEDULE:",
            "-" * 40,
            "• Review in 4 weeks",
            "• Reassessment in 3 months",
            "",
            "CARE TEAM:",
            "-" * 40,
            "• General Practitioner",
            "• Practice Nurse",
            "• Allied Health as required",
            "",
            "=" * 60,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ])
        
        return "\n".join(lines)
    
    def generate_medicare_claim(self, consultation_id: str, consultation_data: Dict[str, Any]) -> str:
        """
        生成Medicare账单（基于诊疗记录）
        
        Args:
            consultation_id: 诊疗ID
            consultation_data: 诊疗数据
            
        Returns:
            文档路径
        """
        logger.info(f"从诊疗记录生成Medicare账单: {consultation_id}")
        
        # 构建账单数据
        mbs_items = consultation_data.get('mbs_recommendations', [])
        if not mbs_items:
            logger.warning("没有MBS推荐项目，无法生成账单")
            return None
        
        claim_data = {
            "claim_id": f"CLM-{consultation_id}",
            "claim_date": datetime.now().isoformat(),
            "consultation_date": consultation_data.get('consultation_date', datetime.now().isoformat()),
            "provider": {
                "provider_number": consultation_data.get('provider_id', 'Unknown'),
                "name": f"Dr. {consultation_data.get('provider_id', 'Provider')}"
            },
            "patient": {
                "medicare_number": "0000000000",  # 示例
                "name": f"Patient {consultation_data.get('patient_id', 'Unknown')}",
                "dob": "1980-01-01"  # 示例
            },
            "items": [
                {
                    "item_number": item.get('item_number'),
                    "description": item.get('description'),
                    "fee": 0,  # 需要从MBS数据中获取
                    "benefit": 0  # 需要从MBS数据中获取
                }
                for item in mbs_items[:3]  # 最多3个项目
            ],
            "total_fee": 0,
            "total_benefit": 0
        }
        
        return self.generate_claim_document(claim_data['claim_id'], claim_data)
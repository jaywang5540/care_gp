from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class MBSItem(BaseModel):
    """MBS项目数据模型"""
    item_number: str = Field(..., description="MBS项目编号")
    description: str = Field(..., description="项目描述")
    category: Optional[str] = Field(None, description="项目类别")
    fee: Optional[float] = Field(None, description="费用")
    schedule_fee: Optional[float] = Field(None, description="计划费用")
    benefit: Optional[float] = Field(None, description="医保补贴")
    
    class Config:
        json_schema_extra = {
            "example": {
                "item_number": "23",
                "description": "Level B consultation",
                "category": "A1",
                "fee": 40.85,
                "schedule_fee": 40.85,
                "benefit": 100
            }
        }

class MBSRecommendation(BaseModel):
    """MBS推荐结果"""
    item_number: str = Field(..., description="推荐的MBS项目编号")
    description: str = Field(..., description="项目描述")
    confidence: float = Field(..., ge=0, le=1, description="置信度(0-1)")
    reason: str = Field(..., description="推荐理由")
    compliance_notes: Optional[List[str]] = Field(None, description="合规注意事项")
    
    class Config:
        json_schema_extra = {
            "example": {
                "item_number": "23",
                "description": "Level B consultation",
                "confidence": 0.95,
                "reason": "Standard consultation lasting 10-20 minutes",
                "compliance_notes": ["Valid for GP consultations", "Cannot be billed with item 24"]
            }
        }

class MBSRecommendRequest(BaseModel):
    """MBS推荐请求"""
    consultation_text: str = Field(..., description="诊疗对话文本")
    patient_age: Optional[int] = Field(None, description="患者年龄")
    consultation_duration: Optional[int] = Field(None, description="诊疗时长(分钟)")
    consultation_type: Optional[str] = Field(None, description="诊疗类型")
    
    class Config:
        json_schema_extra = {
            "example": {
                "consultation_text": "Patient presenting with acute upper respiratory symptoms...",
                "patient_age": 45,
                "consultation_duration": 15,
                "consultation_type": "standard"
            }
        }

class MBSRecommendResponse(BaseModel):
    """MBS推荐响应"""
    recommendations: List[MBSRecommendation] = Field(..., description="推荐列表")
    extracted_info: Dict[str, Any] = Field(default_factory=dict, description="提取的关键信息")
    
class ClaimGenerationRequest(BaseModel):
    """账单生成请求"""
    mbs_items: List[str] = Field(..., description="MBS项目编号列表")
    patient_details: Dict[str, Any] = Field(..., description="患者信息")
    provider_details: Dict[str, Any] = Field(..., description="医生信息")
    consultation_date: datetime = Field(default_factory=datetime.now, description="诊疗日期")
    
    class Config:
        json_schema_extra = {
            "example": {
                "mbs_items": ["23", "721"],
                "patient_details": {
                    "medicare_number": "1234567890",
                    "name": "John Doe",
                    "dob": "1980-01-01"
                },
                "provider_details": {
                    "provider_number": "0000000A",
                    "name": "Dr. Smith"
                },
                "consultation_date": "2024-01-15T10:30:00"
            }
        }

class ClaimGenerationResponse(BaseModel):
    """账单生成响应"""
    claim_id: str = Field(..., description="账单ID")
    claim_payload: Dict[str, Any] = Field(..., description="账单数据")
    total_fee: float = Field(..., description="总费用")
    total_benefit: float = Field(..., description="总医保补贴")
    document_path: Optional[str] = Field(None, description="生成的文档路径")
    
class ComplianceCheckRequest(BaseModel):
    """合规检查请求"""
    mbs_items: List[str] = Field(..., description="MBS项目编号列表")
    patient_history: Optional[Dict[str, Any]] = Field(None, description="患者历史记录")
    consultation_details: Dict[str, Any] = Field(..., description="诊疗详情")
    
class ComplianceCheckResponse(BaseModel):
    """合规检查响应"""
    is_compliant: bool = Field(..., description="是否合规")
    warnings: List[str] = Field(default_factory=list, description="警告信息")
    errors: List[str] = Field(default_factory=list, description="错误信息")
    suggestions: List[str] = Field(default_factory=list, description="建议")
    details: Dict[str, Any] = Field(default_factory=dict, description="详细信息")
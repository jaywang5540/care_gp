from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class InputType(str, Enum):
    """输入类型枚举"""
    TEXT = "text"
    VOICE = "voice"

class ConsultationStatus(str, Enum):
    """诊疗状态枚举"""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ConsultationInput(BaseModel):
    """诊疗输入数据模型"""
    input_type: InputType = Field(InputType.TEXT, description="输入类型")
    content: str = Field(..., description="输入内容(文本或语音转文本)")
    patient_id: Optional[str] = Field(None, description="患者ID")
    provider_id: Optional[str] = Field(None, description="医生ID")
    consultation_date: datetime = Field(default_factory=datetime.now, description="诊疗日期")
    duration_minutes: Optional[int] = Field(None, description="诊疗时长(分钟)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "input_type": "text",
                "content": "Patient presenting with headache for 3 days, no fever...",
                "patient_id": "P123456",
                "provider_id": "D789012",
                "duration_minutes": 15
            }
        }

class ConsultationRecord(BaseModel):
    """诊疗记录数据模型"""
    consultation_id: str = Field(..., description="诊疗记录ID")
    patient_id: Optional[str] = Field(None, description="患者ID")
    provider_id: Optional[str] = Field(None, description="医生ID")
    consultation_date: datetime = Field(..., description="诊疗日期")
    duration_minutes: Optional[int] = Field(None, description="诊疗时长")
    status: ConsultationStatus = Field(..., description="诊疗状态")
    
    # 诊疗内容
    chief_complaint: Optional[str] = Field(None, description="主诉")
    history_present_illness: Optional[str] = Field(None, description="现病史")
    examination_findings: Optional[str] = Field(None, description="检查发现")
    diagnosis: Optional[List[str]] = Field(None, description="诊断")
    treatment_plan: Optional[str] = Field(None, description="治疗计划")
    
    # MBS相关
    recommended_mbs_items: Optional[List[str]] = Field(None, description="推荐的MBS项目")
    selected_mbs_items: Optional[List[str]] = Field(None, description="选定的MBS项目")
    
    # 原始数据
    raw_input: Optional[str] = Field(None, description="原始输入")
    processed_data: Optional[Dict[str, Any]] = Field(None, description="处理后的数据")
    
    # 时间戳
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "consultation_id": "C20240115-001",
                "patient_id": "P123456",
                "provider_id": "D789012",
                "consultation_date": "2024-01-15T10:30:00",
                "duration_minutes": 15,
                "status": "completed",
                "chief_complaint": "Headache",
                "diagnosis": ["Tension headache"],
                "recommended_mbs_items": ["23"]
            }
        }

class ProcessConsultationRequest(BaseModel):
    """处理诊疗请求"""
    consultation_input: ConsultationInput = Field(..., description="诊疗输入")
    auto_recommend_mbs: bool = Field(True, description="是否自动推荐MBS项目")
    generate_documents: bool = Field(False, description="是否生成文档")
    
class ProcessConsultationResponse(BaseModel):
    """处理诊疗响应"""
    consultation_id: str = Field(..., description="诊疗记录ID")
    extracted_info: Dict[str, Any] = Field(..., description="提取的信息")
    mbs_recommendations: Optional[List[Dict[str, Any]]] = Field(None, description="MBS推荐")
    generated_documents: Optional[List[str]] = Field(None, description="生成的文档路径")
    status: str = Field(..., description="处理状态")
    
class DocumentGenerationRequest(BaseModel):
    """文档生成请求"""
    consultation_id: str = Field(..., description="诊疗记录ID")
    document_types: List[str] = Field(..., description="要生成的文档类型")
    
    class Config:
        json_schema_extra = {
            "example": {
                "consultation_id": "C20240115-001",
                "document_types": ["referral_letter", "care_plan", "medicare_claim"]
            }
        }

class DocumentGenerationResponse(BaseModel):
    """文档生成响应"""
    consultation_id: str = Field(..., description="诊疗记录ID")
    generated_documents: Dict[str, str] = Field(..., description="生成的文档(类型->路径)")
    status: str = Field(..., description="生成状态")
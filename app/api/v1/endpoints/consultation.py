from fastapi import APIRouter, HTTPException, Depends
from app.schemas.consultation import (
    ConsultationInput,
    ConsultationRecord,
    ProcessConsultationRequest,
    ProcessConsultationResponse,
    DocumentGenerationRequest,
    DocumentGenerationResponse
)
from app.schemas.common_response import SuccessResponse
from app.utils.response import ResponseUtil
from app.services.text_processor import TextProcessor
from app.services.mbs_service import MBSService
from app.services.document_generator import DocumentGenerator
from app.core.config import settings
from typing import List, Dict, Any
import json
import uuid
from datetime import datetime
from pathlib import Path

router = APIRouter()

# 依赖注入
def get_text_processor() -> TextProcessor:
    return TextProcessor()

def get_mbs_service() -> MBSService:
    return MBSService()

def get_document_generator() -> DocumentGenerator:
    return DocumentGenerator()

@router.post("/process", response_model=SuccessResponse[ProcessConsultationResponse], summary="处理诊疗输入")
async def process_consultation(
    request: ProcessConsultationRequest,
    text_processor: TextProcessor = Depends(get_text_processor),
    mbs_service: MBSService = Depends(get_mbs_service),
    document_generator: DocumentGenerator = Depends(get_document_generator)
):
    """
    处理诊疗对话输入
    
    功能：
    - 提取关键信息
    - 自动推荐MBS项目
    - 可选生成文档
    """
    try:
        # 生成诊疗ID
        consultation_id = f"C{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        # 提取诊疗信息
        extracted_info = text_processor.extract_consultation_info(
            request.consultation_input.content
        )
        
        # 添加输入中的额外信息
        extracted_info.update({
            "patient_id": request.consultation_input.patient_id,
            "provider_id": request.consultation_input.provider_id,
            "consultation_date": request.consultation_input.consultation_date.isoformat(),
            "duration_minutes": request.consultation_input.duration_minutes
        })
        
        # 推荐MBS项目（如果启用）
        mbs_recommendations = []
        if request.auto_recommend_mbs:
            recommendations = mbs_service.recommend_mbs_items(extracted_info)
            mbs_recommendations = [
                {
                    "item_number": rec.item_number,
                    "description": rec.description,
                    "confidence": rec.confidence,
                    "reason": rec.reason
                }
                for rec in recommendations
            ]
        
        # 保存诊疗记录
        consultation_record = {
            "consultation_id": consultation_id,
            "patient_id": request.consultation_input.patient_id,
            "provider_id": request.consultation_input.provider_id,
            "consultation_date": request.consultation_input.consultation_date.isoformat(),
            "duration_minutes": request.consultation_input.duration_minutes,
            "status": "completed",
            "raw_input": request.consultation_input.content,
            "extracted_info": extracted_info,
            "mbs_recommendations": mbs_recommendations,
            "created_at": datetime.now().isoformat()
        }
        
        # 保存到文件
        save_consultation_record(consultation_id, consultation_record)
        
        # 生成文档（如果需要）
        generated_documents = []
        if request.generate_documents:
            # 这里可以生成各种文档
            doc_path = document_generator.generate_consultation_summary(
                consultation_id, 
                consultation_record
            )
            if doc_path:
                generated_documents.append(doc_path)
        
        # 构建响应
        response = ProcessConsultationResponse(
            consultation_id=consultation_id,
            extracted_info=extracted_info,
            mbs_recommendations=mbs_recommendations,
            generated_documents=generated_documents,
            status="success"
        )
        
        return ResponseUtil.success(
            data=response,
            message="诊疗处理成功"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/records", response_model=SuccessResponse[List[Dict[str, Any]]], summary="获取诊疗记录列表")
async def get_consultation_records(
    patient_id: str = None,
    provider_id: str = None,
    date_from: str = None,
    date_to: str = None
):
    """
    获取诊疗记录列表
    
    支持按患者、医生、日期范围筛选
    """
    try:
        records = load_consultation_records(
            patient_id=patient_id,
            provider_id=provider_id,
            date_from=date_from,
            date_to=date_to
        )
        
        return ResponseUtil.success(
            data=records,
            message=f"获取到 {len(records)} 条诊疗记录"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/records/{consultation_id}", response_model=SuccessResponse[Dict[str, Any]], summary="获取单个诊疗记录")
async def get_consultation_record(consultation_id: str):
    """
    根据ID获取诊疗记录详情
    """
    try:
        record = load_consultation_record(consultation_id)
        if not record:
            raise HTTPException(status_code=404, detail=f"诊疗记录 {consultation_id} 不存在")
        
        return ResponseUtil.success(
            data=record,
            message="获取诊疗记录成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-documents", response_model=SuccessResponse[DocumentGenerationResponse], summary="生成诊疗文档")
async def generate_consultation_documents(
    request: DocumentGenerationRequest,
    document_generator: DocumentGenerator = Depends(get_document_generator)
):
    """
    为诊疗记录生成各种文档
    
    支持的文档类型：
    - referral_letter: 转诊信
    - care_plan: 护理计划
    - medicare_claim: Medicare账单
    - summary: 诊疗摘要
    """
    try:
        # 加载诊疗记录
        record = load_consultation_record(request.consultation_id)
        if not record:
            raise HTTPException(status_code=404, detail=f"诊疗记录 {request.consultation_id} 不存在")
        
        # 生成文档
        generated_documents = {}
        for doc_type in request.document_types:
            if doc_type == "referral_letter":
                path = document_generator.generate_referral_letter(request.consultation_id, record)
            elif doc_type == "care_plan":
                path = document_generator.generate_care_plan(request.consultation_id, record)
            elif doc_type == "medicare_claim":
                path = document_generator.generate_medicare_claim(request.consultation_id, record)
            elif doc_type == "summary":
                path = document_generator.generate_consultation_summary(request.consultation_id, record)
            else:
                continue
            
            if path:
                generated_documents[doc_type] = path
        
        # 构建响应
        response = DocumentGenerationResponse(
            consultation_id=request.consultation_id,
            generated_documents=generated_documents,
            status="success"
        )
        
        return ResponseUtil.success(
            data=response,
            message=f"生成了 {len(generated_documents)} 个文档"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 辅助函数
def save_consultation_record(consultation_id: str, record: Dict[str, Any]):
    """保存诊疗记录到文件"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    date_path = settings.CONSULTATIONS_PATH / date_str
    date_path.mkdir(parents=True, exist_ok=True)
    
    file_path = date_path / f"{consultation_id}.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(record, f, ensure_ascii=False, indent=2)

def load_consultation_record(consultation_id: str) -> Dict[str, Any]:
    """加载单个诊疗记录"""
    # 搜索所有日期目录
    for date_dir in settings.CONSULTATIONS_PATH.glob("*"):
        if date_dir.is_dir():
            file_path = date_dir / f"{consultation_id}.json"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
    return None

def load_consultation_records(
    patient_id: str = None,
    provider_id: str = None,
    date_from: str = None,
    date_to: str = None
) -> List[Dict[str, Any]]:
    """加载诊疗记录列表"""
    records = []
    
    # 遍历所有日期目录
    for date_dir in sorted(settings.CONSULTATIONS_PATH.glob("*")):
        if date_dir.is_dir():
            # 检查日期范围
            date_str = date_dir.name
            if date_from and date_str < date_from:
                continue
            if date_to and date_str > date_to:
                continue
            
            # 加载该日期的所有记录
            for file_path in date_dir.glob("*.json"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    record = json.load(f)
                    
                    # 筛选条件
                    if patient_id and record.get("patient_id") != patient_id:
                        continue
                    if provider_id and record.get("provider_id") != provider_id:
                        continue
                    
                    records.append(record)
    
    return records
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.medicare import (
    MBSItem,
    MBSRecommendRequest,
    MBSRecommendResponse,
    MBSRecommendation,
    ClaimGenerationRequest,
    ClaimGenerationResponse,
    ComplianceCheckRequest,
    ComplianceCheckResponse
)
from app.schemas.common_response import SuccessResponse
from app.utils.response import ResponseUtil
from app.services.mbs_service import MBSService
from app.services.text_processor import TextProcessor
from app.services.document_generator import DocumentGenerator
from typing import List, Dict, Any
import uuid
from datetime import datetime

router = APIRouter()

# 依赖注入
def get_mbs_service() -> MBSService:
    return MBSService()

def get_text_processor() -> TextProcessor:
    return TextProcessor()

def get_document_generator() -> DocumentGenerator:
    return DocumentGenerator()

@router.get("/mbs-items", response_model=SuccessResponse[List[MBSItem]], summary="获取MBS项目列表")
async def get_mbs_items(
    category: str = None,
    search: str = None,
    mbs_service: MBSService = Depends(get_mbs_service)
):
    """
    获取MBS项目列表
    
    - **category**: 项目类别筛选
    - **search**: 搜索关键词
    """
    try:
        items = mbs_service.get_mbs_items(category=category, search=search)
        return ResponseUtil.success(
            data=items,
            message=f"获取到 {len(items)} 个MBS项目"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mbs-items/{item_number}", response_model=SuccessResponse[MBSItem], summary="获取单个MBS项目")
async def get_mbs_item(
    item_number: str,
    mbs_service: MBSService = Depends(get_mbs_service)
):
    """
    根据项目编号获取MBS项目详情
    
    - **item_number**: MBS项目编号
    """
    try:
        item = mbs_service.get_mbs_item(item_number)
        if not item:
            raise HTTPException(status_code=404, detail=f"MBS项目 {item_number} 不存在")
        return ResponseUtil.success(
            data=item,
            message="获取MBS项目成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/recommend", response_model=SuccessResponse[MBSRecommendResponse], summary="推荐MBS编码")
async def recommend_mbs_codes(
    request: MBSRecommendRequest,
    mbs_service: MBSService = Depends(get_mbs_service),
    text_processor: TextProcessor = Depends(get_text_processor)
):
    """
    根据诊疗对话推荐合适的MBS编码
    
    处理流程：
    1. 从文本中提取关键信息
    2. 匹配合适的MBS项目
    3. 返回推荐列表和置信度
    """
    try:
        # 提取关键信息
        extracted_info = text_processor.extract_consultation_info(request.consultation_text)
        
        # 添加额外的请求信息
        if request.patient_age:
            extracted_info["patient_age"] = request.patient_age
        if request.consultation_duration:
            extracted_info["consultation_duration"] = request.consultation_duration
        if request.consultation_type:
            extracted_info["consultation_type"] = request.consultation_type
        
        # 推荐MBS项目
        recommendations = mbs_service.recommend_mbs_items(extracted_info)
        
        # 构建响应
        response = MBSRecommendResponse(
            recommendations=recommendations,
            extracted_info=extracted_info
        )
        
        return ResponseUtil.success(
            data=response,
            message=f"推荐了 {len(recommendations)} 个MBS项目"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-claim", response_model=SuccessResponse[ClaimGenerationResponse], summary="生成账单")
async def generate_claim(
    request: ClaimGenerationRequest,
    mbs_service: MBSService = Depends(get_mbs_service),
    document_generator: DocumentGenerator = Depends(get_document_generator)
):
    """
    生成Medicare账单
    
    根据选定的MBS项目和患者信息生成可提交的账单
    """
    try:
        # 验证MBS项目
        total_fee = 0.0
        total_benefit = 0.0
        validated_items = []
        
        for item_number in request.mbs_items:
            item = mbs_service.get_mbs_item(item_number)
            if item:
                validated_items.append(item)
                total_fee += item.get("fee", 0)
                total_benefit += item.get("benefit", 0)
        
        if not validated_items:
            raise HTTPException(status_code=400, detail="没有有效的MBS项目")
        
        # 生成账单ID
        claim_id = f"CLM-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        # 构建账单数据
        claim_payload = {
            "claim_id": claim_id,
            "claim_date": datetime.now().isoformat(),
            "provider": request.provider_details,
            "patient": request.patient_details,
            "consultation_date": request.consultation_date.isoformat(),
            "items": [
                {
                    "item_number": item["item_number"],
                    "description": item["description"],
                    "fee": item.get("fee", 0),
                    "benefit": item.get("benefit", 0)
                }
                for item in validated_items
            ],
            "total_fee": total_fee,
            "total_benefit": total_benefit
        }
        
        # 生成文档
        document_path = document_generator.generate_claim_document(claim_id, claim_payload)
        
        # 构建响应
        response = ClaimGenerationResponse(
            claim_id=claim_id,
            claim_payload=claim_payload,
            total_fee=total_fee,
            total_benefit=total_benefit,
            document_path=document_path
        )
        
        return ResponseUtil.success(
            data=response,
            message="账单生成成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/check-compliance", response_model=SuccessResponse[ComplianceCheckResponse], summary="合规检查")
async def check_compliance(
    request: ComplianceCheckRequest,
    mbs_service: MBSService = Depends(get_mbs_service)
):
    """
    检查MBS项目组合的合规性
    
    验证：
    - 项目组合是否允许
    - 时间限制
    - 患者条件要求
    """
    try:
        # 执行合规检查
        result = mbs_service.check_compliance(
            mbs_items=request.mbs_items,
            patient_history=request.patient_history,
            consultation_details=request.consultation_details
        )
        
        # 构建响应
        response = ComplianceCheckResponse(
            is_compliant=result["is_compliant"],
            warnings=result.get("warnings", []),
            errors=result.get("errors", []),
            suggestions=result.get("suggestions", []),
            details=result.get("details", {})
        )
        
        return ResponseUtil.success(
            data=response,
            message="合规检查完成"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
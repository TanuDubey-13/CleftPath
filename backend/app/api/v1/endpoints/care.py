from datetime import date
from typing import Optional
import uuid
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.care import (
    CareOverviewResponse,
    FeedingLogCreateRequest,
    FeedingLogResponse,
    FeedingLogUpdateRequest,
    GrowthRecordCreateRequest,
    GrowthRecordResponse,
    GrowthRecordUpdateRequest,
    NAMTapingLogCreateRequest,
    NAMTapingLogResponse,
    NAMTapingLogUpdateRequest,
    PaginatedFeedingLogsResponse,
    PaginatedGrowthRecordsResponse,
    PaginatedNAMLogsResponse,
)
from app.schemas.common import StandardResponse
from app.services.care_service import CareService

router = APIRouter()


# ============================================================================
# Care Overview
# ============================================================================

@router.get(
    "/overview",
    response_model=StandardResponse[CareOverviewResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Care Overview",
    description="Retrieve aggregated metrics across feeding, growth, and NAM along with safety care guidance.",
)
async def get_care_overview(
    patient_id: Optional[uuid.UUID] = Query(default=None, description="Patient UUID"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[CareOverviewResponse]:
    overview = await CareService.get_care_overview(
        db=db,
        current_user=current_user,
        patient_id=patient_id,
    )
    return StandardResponse(success=True, data=overview)


# ============================================================================
# Feeding Log Endpoints
# ============================================================================

@router.get(
    "/feeding",
    response_model=StandardResponse[PaginatedFeedingLogsResponse],
    status_code=status.HTTP_200_OK,
    summary="List Feeding Logs",
    description="Retrieve feeding records with date filtering and pagination.",
)
async def list_feeding_logs(
    patient_id: Optional[uuid.UUID] = Query(default=None, description="Patient UUID"),
    start_date: Optional[date] = Query(default=None, description="Filter start date"),
    end_date: Optional[date] = Query(default=None, description="Filter end date"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[PaginatedFeedingLogsResponse]:
    result = await CareService.list_feeding_logs(
        db=db,
        current_user=current_user,
        patient_id=patient_id,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
    )
    return StandardResponse(success=True, data=result)


@router.get(
    "/feeding/{log_id}",
    response_model=StandardResponse[FeedingLogResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Feeding Log Detail",
)
async def get_feeding_log(
    log_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[FeedingLogResponse]:
    log = await CareService.get_feeding_log_by_id(
        db=db,
        log_id=log_id,
        current_user=current_user,
    )
    return StandardResponse(success=True, data=log)


@router.post(
    "/feeding",
    response_model=StandardResponse[FeedingLogResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create Feeding Log",
)
async def create_feeding_log(
    payload: FeedingLogCreateRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[FeedingLogResponse]:
    log = await CareService.create_feeding_log(
        db=db,
        payload=payload,
        current_user=current_user,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return StandardResponse(success=True, data=log)


@router.patch(
    "/feeding/{log_id}",
    response_model=StandardResponse[FeedingLogResponse],
    status_code=status.HTTP_200_OK,
    summary="Update Feeding Log",
)
async def update_feeding_log(
    log_id: uuid.UUID,
    payload: FeedingLogUpdateRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[FeedingLogResponse]:
    log = await CareService.update_feeding_log(
        db=db,
        log_id=log_id,
        payload=payload,
        current_user=current_user,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return StandardResponse(success=True, data=log)


@router.delete(
    "/feeding/{log_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Feeding Log",
)
async def delete_feeding_log(
    log_id: uuid.UUID,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    await CareService.delete_feeding_log(
        db=db,
        log_id=log_id,
        current_user=current_user,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )


# ============================================================================
# Growth Records Endpoints
# ============================================================================

@router.get(
    "/growth",
    response_model=StandardResponse[PaginatedGrowthRecordsResponse],
    status_code=status.HTTP_200_OK,
    summary="List Growth Records",
    description="Retrieve weight, length, and head circumference measurement history.",
)
async def list_growth_records(
    patient_id: Optional[uuid.UUID] = Query(default=None, description="Patient UUID"),
    start_date: Optional[date] = Query(default=None, description="Filter start date"),
    end_date: Optional[date] = Query(default=None, description="Filter end date"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[PaginatedGrowthRecordsResponse]:
    result = await CareService.list_growth_records(
        db=db,
        current_user=current_user,
        patient_id=patient_id,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
    )
    return StandardResponse(success=True, data=result)


@router.get(
    "/growth/{record_id}",
    response_model=StandardResponse[GrowthRecordResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Growth Record Detail",
)
async def get_growth_record(
    record_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[GrowthRecordResponse]:
    record = await CareService.get_growth_record_by_id(
        db=db,
        record_id=record_id,
        current_user=current_user,
    )
    return StandardResponse(success=True, data=record)


@router.post(
    "/growth",
    response_model=StandardResponse[GrowthRecordResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create Growth Record",
)
async def create_growth_record(
    payload: GrowthRecordCreateRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[GrowthRecordResponse]:
    record = await CareService.create_growth_record(
        db=db,
        payload=payload,
        current_user=current_user,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return StandardResponse(success=True, data=record)


@router.patch(
    "/growth/{record_id}",
    response_model=StandardResponse[GrowthRecordResponse],
    status_code=status.HTTP_200_OK,
    summary="Update Growth Record",
)
async def update_growth_record(
    record_id: uuid.UUID,
    payload: GrowthRecordUpdateRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[GrowthRecordResponse]:
    record = await CareService.update_growth_record(
        db=db,
        record_id=record_id,
        payload=payload,
        current_user=current_user,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return StandardResponse(success=True, data=record)


@router.delete(
    "/growth/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Growth Record",
)
async def delete_growth_record(
    record_id: uuid.UUID,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    await CareService.delete_growth_record(
        db=db,
        record_id=record_id,
        current_user=current_user,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )


# ============================================================================
# NAM / Taping Endpoints
# ============================================================================

@router.get(
    "/nam",
    response_model=StandardResponse[PaginatedNAMLogsResponse],
    status_code=status.HTTP_200_OK,
    summary="List NAM / Taping Logs",
    description="Retrieve daily Nasoalveolar Molding wear hours and skin condition logs.",
)
async def list_nam_logs(
    patient_id: Optional[uuid.UUID] = Query(default=None, description="Patient UUID"),
    start_date: Optional[date] = Query(default=None, description="Filter start date"),
    end_date: Optional[date] = Query(default=None, description="Filter end date"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[PaginatedNAMLogsResponse]:
    result = await CareService.list_nam_logs(
        db=db,
        current_user=current_user,
        patient_id=patient_id,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
    )
    return StandardResponse(success=True, data=result)


@router.get(
    "/nam/{log_id}",
    response_model=StandardResponse[NAMTapingLogResponse],
    status_code=status.HTTP_200_OK,
    summary="Get NAM Log Detail",
)
async def get_nam_log(
    log_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[NAMTapingLogResponse]:
    log = await CareService.get_nam_log_by_id(
        db=db,
        log_id=log_id,
        current_user=current_user,
    )
    return StandardResponse(success=True, data=log)


@router.post(
    "/nam",
    response_model=StandardResponse[NAMTapingLogResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create NAM Log",
)
async def create_nam_log(
    payload: NAMTapingLogCreateRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[NAMTapingLogResponse]:
    log = await CareService.create_nam_log(
        db=db,
        payload=payload,
        current_user=current_user,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return StandardResponse(success=True, data=log)


@router.patch(
    "/nam/{log_id}",
    response_model=StandardResponse[NAMTapingLogResponse],
    status_code=status.HTTP_200_OK,
    summary="Update NAM Log",
)
async def update_nam_log(
    log_id: uuid.UUID,
    payload: NAMTapingLogUpdateRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[NAMTapingLogResponse]:
    log = await CareService.update_nam_log(
        db=db,
        log_id=log_id,
        payload=payload,
        current_user=current_user,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return StandardResponse(success=True, data=log)


@router.delete(
    "/nam/{log_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete NAM Log",
)
async def delete_nam_log(
    log_id: uuid.UUID,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    await CareService.delete_nam_log(
        db=db,
        log_id=log_id,
        current_user=current_user,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

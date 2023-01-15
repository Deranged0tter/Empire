from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import Response
from starlette.status import HTTP_204_NO_CONTENT

from empire.server.api.api_router import APIRouter
from empire.server.api.jwt_auth import get_current_active_user
from empire.server.api.v2.bypass.bypass_dto import (
    Bypass,
    Bypasses,
    BypassPostRequest,
    BypassUpdateRequest,
    domain_to_dto_bypass,
)
from empire.server.api.v2.shared_dependencies import get_db
from empire.server.api.v2.shared_dto import BadRequestResponse, NotFoundResponse
from empire.server.core.db import models
from empire.server.server import main

bypass_service = main.bypassesv2

router = APIRouter(
    prefix="/api/v2/bypasses",
    tags=["bypasses"],
    responses={
        404: {"description": "Not found", "model": NotFoundResponse},
        400: {"description": "Bad request", "model": BadRequestResponse},
    },
    dependencies=[Depends(get_current_active_user)],
)


async def get_bypass(uid: int, db: Session = Depends(get_db)):
    bypass = bypass_service.get_by_id(db, uid)

    if bypass:
        return bypass

    raise HTTPException(404, f"Bypass not found for id {uid}")


@router.get("/{uid}", response_model=Bypass)
async def read_bypass(uid: int, db_bypass: models.Bypass = Depends(get_bypass)):
    return domain_to_dto_bypass(db_bypass)


@router.get("/", response_model=Bypasses)
async def read_bypasses(db: Session = Depends(get_db)):
    bypasses = list(map(lambda x: domain_to_dto_bypass(x), bypass_service.get_all(db)))

    return {"records": bypasses}


@router.post("/", status_code=201, response_model=Bypass)
async def create_bypass(bypass_req: BypassPostRequest, db: Session = Depends(get_db)):
    resp, err = bypass_service.create_bypass(db, bypass_req)

    if err:
        raise HTTPException(status_code=400, detail=err)

    return domain_to_dto_bypass(resp)


@router.put("/{uid}", response_model=Bypass)
async def update_bypass(
    uid: int,
    bypass_req: BypassUpdateRequest,
    db: Session = Depends(get_db),
    db_bypass: models.Bypass = Depends(get_bypass),
):
    resp, err = bypass_service.update_bypass(db, db_bypass, bypass_req)

    if err:
        raise HTTPException(status_code=400, detail=err)

    return domain_to_dto_bypass(resp)


@router.delete("/{uid}", status_code=HTTP_204_NO_CONTENT, response_class=Response)
async def delete_bypass(
    uid: str,
    db: Session = Depends(get_db),
    db_bypass: models.Bypass = Depends(get_bypass),
):
    bypass_service.delete_bypass(db, db_bypass)

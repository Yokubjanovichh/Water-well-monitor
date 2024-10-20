import random
from typing import List
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.core.database import engine, get_session
from app.schemas.wells_schemas import WellSchema, WellDevSchema
from app.schemas.message_schemas import MessageSchema
from app.services.crud.well_crud import get_well_by_number
from app.models.models import (
    UserModel,
    WellsModel,
    MessageModel,
    StatementModel,
    Base,
)

settings_router = APIRouter()


@settings_router.get("/database/init")
async def init_database():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        return JSONResponse(content={"database": "initialized"})


@settings_router.get("/database/reset")
async def reset_database():
    async with engine.begin() as conn:

        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        return JSONResponse(content={"database": "reseted"})


@settings_router.post("/database/init/wellls")
async def init_wells_data_database(
    wells: List[WellSchema],
):
    async with get_session() as session:
        for well in wells:
            new_well = WellsModel(
                well_id=str(well.well_id),
                time=well.created_time,
                **well.model_dump(exclude={"well_id", "created_time"}),
            )
            session.add(new_well)
            await session.commit()


@settings_router.post("/database/init/wellls/dev")
async def init_wells_data_database_dev(
    wells: List[WellDevSchema],
):
    async with get_session() as session:
        for well in wells:
            new_well = WellsModel(
                well_id=str(well.well_id),
                **well.model_dump(exclude={"well_id"}),
            )
            session.add(new_well)
            await session.commit()


@settings_router.post("/database/init/messages")
async def init_messages_data_database(
    messages: List[MessageSchema],
):
    async with get_session() as session:
        for message in messages:
            well = await get_well_by_number(message.number)
            if not well:
                continue
            message.water_level = str(
                int(str(well.depth)) - round(float(message.water_level))
            )
            if well.salinity_start:  # type: ignore
                message.salinity = str(
                    random.uniform(
                        float(str(well.salinity_start)), float(str(well.salinity_end))
                    )
                )
            message = MessageModel(
                message_id=str(message.message_id),
                received_at=message.received_at,
                **message.model_dump(exclude={"message_id", "received_at"}),
            )
            session.add(message)
            await session.commit()
from contextlib import asynccontextmanager
from datetime import datetime
import json
from typing import Dict, List, Union

import aiofiles
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase


class Base(AsyncAttrs, DeclarativeBase):
    pass


# region error
class ErrorResponse(BaseModel):
    detail: str


# region Base
class BaseResponse(BaseModel):
    data: Union[List, Dict, str] = Field([], description="Data of the request")
    message: str = Field(..., examples=["success"], description="Status of the request")

def get_engine(db_url: str):
    return create_async_engine(db_url)

engine = get_engine('sqlite+aiosqlite:///yoruba_transcriptions.db')

async def init_db():
    from models.yoruba_models import Transcription
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@asynccontextmanager
async def get_session():
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
        
async def load_data():
    from models.yoruba_models import Transcription
    async with get_session() as session:
        transcriptions = await session.execute(select(Transcription))   
        transcriptions = transcriptions.scalars().all()
        paths = {transcription.path for transcription in transcriptions}
        async with aiofiles.open('yoruba_transcriptions.json', mode='r') as file:
            data = await file.read()
            transcriptions: List[Dict] = json.loads(data)
            for transcription in transcriptions:
                if transcription.get("path") in paths:
                    continue
                data = {    
                    "transcript": transcription.get("transcript", ""),
                    "last_edited_by": "system",
                    "last_edited_at": datetime.now(),   
                    "language": transcription.get("language", "yoruba"),
                    "clean_text": transcription.get("clean_text", ""),
                    "path": transcription.get("path", ""),
                    "old_text_rating": transcription.get("old_text_rating", 0),
                    "new_text_rating": transcription.get("new_text_rating", 0),
                    "cleaned": transcription.get("cleaned", False),
                    "has_music": transcription.get("has_music", False),
                    "multispeaker": transcription.get("multispeaker", False),
                    "crowd": transcription.get("crowd", False), 
                }
                transcription = Transcription(**data)
                session.add(transcription)
        await session.commit()  

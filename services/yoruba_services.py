from models.yoruba_models import Transcription
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
class TranscriptionService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_transcription(self, transcription: Transcription):
        async with self.session as session:
            session.add(transcription)
            await session.commit()
            return transcription

    async def get_transcription(self, transcription_id: int):
        async with self.session as session:
            return await session.get(Transcription, transcription_id)

    async def update_transcription(self, transcription_id: int, transcription: Transcription):
        async with self.session as session:
            await session.merge(transcription)
            await session.commit()
            return transcription

    async def delete_transcription(self, transcription_id: int):
        async with self.session as session:
            transcription = await session.get(Transcription, transcription_id)
            if transcription:
                await session.delete(transcription)
                await session.commit()
                return True
            return False

    async def get_paginated_transcriptions(self, page: int, per_page: int):
        async with self.session as session:
            query = select(Transcription).offset((page - 1) * per_page).limit(per_page)
            result = await session.execute(query)
            transcriptions = result.scalars().all()
            total = await session.scalar(select(func.count(Transcription.id)))
            return [transcription.to_dict() for transcription in transcriptions], total
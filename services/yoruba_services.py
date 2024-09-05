from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.yoruba_models import Transcription, UpdateTranscriptionRequest


class TranscriptionService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_transcription(self, transcription: Transcription):
        self.session.add(transcription)
        await self.session.commit()
        return transcription

    async def get_transcription(self, transcription_id: int):
        stmt = select(Transcription).where(Transcription.id == transcription_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_transcription(
        self, transcription_id: int, transcription: UpdateTranscriptionRequest
    ):
        query = select(Transcription).where(Transcription.id == transcription_id)
        result = await self.session.execute(query)
        existing_transcription = result.scalar_one_or_none()
        print(f"existing_transcription: {existing_transcription}")
        if existing_transcription:
            existing_transcription.cleaned = (
                transcription.cleaned if transcription.clean_text else False
            )
            existing_transcription.clean_text = transcription.clean_text
            existing_transcription.new_text_rating = transcription.new_text_rating
            existing_transcription.old_text_rating = transcription.old_text_rating
            existing_transcription.has_music = transcription.has_music
            existing_transcription.multispeaker = transcription.multispeaker
            existing_transcription.crowd = transcription.crowd
            existing_transcription.last_edited_at = datetime.now()
            print(f"updated transcription: {existing_transcription}")
            await self.session.commit()
            return True, "Transcription updated successfully"
        return False, "Transcription not found"

    async def delete_transcription(self, transcription_id: int):
        transcription = await self.session.get(Transcription, transcription_id)
        if transcription:
            await self.session.delete(transcription)
            await self.session.commit()
            return True
        return False

    async def get_paginated_transcriptions(self, page: int, per_page: int):
        query = (
            select(Transcription)
            .where(Transcription.cleaned == False)
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        result = await self.session.execute(query)
        transcriptions = result.scalars().all()
        total = await self.session.scalar(select(func.count(Transcription.id)))
        return [transcription.to_dict() for transcription in transcriptions], total

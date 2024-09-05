from models.base import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime

from pydantic import BaseModel, Field
from datetime import datetime

# region GetTranscriptionResponse
class GetTranscriptionResponse(BaseModel):
    path: str = Field(..., description="The path to the transcription")
    transcript: str = Field(..., description="The transcript of the audio")
    has_music: bool = Field(..., description="Whether the audio has music")
    multispeaker: bool = Field(..., description="Whether the audio is a multispeaker")
    crowd: bool = Field(..., description="Whether the audio is a crowd")
    last_edited_by: str = Field(..., description="The last editor of the transcription")
    last_edited_at: datetime = Field(..., description="The last edited at time")
    language: str = Field(..., description="The language of the transcription")
    clean_text: str = Field(..., description="The cleaned text")
    cleaned: bool = Field(..., description="Whether the transcription has been cleaned")
    old_text_rating: int = Field(..., description="The old text rating")
    new_text_rating: int = Field(..., description="The new text rating")
# endregion GetTranscriptionResponse

# region GetTranscriptionQueryArgs
class GetTranscriptionQueryArgs(BaseModel):
    page: int = Field(..., description="The page number")
    per_page: int = Field(..., description="The number of items per page")
# endregion GetTranscriptionQueryArgs

# region PaginatedTranscriptionResponse
class PaginatedTranscriptionResponse(BaseModel):
    data: list[GetTranscriptionResponse] = Field(..., description="The list of transcriptions")
    page: int = Field(..., description="The page number")
    per_page: int = Field(..., description="The number of items per page")
    total: int = Field(..., description="The total number of items")
    total_pages: int = Field(..., description="The total number of pages")  
# endregion PaginatedTranscriptionResponse

# region ServeFileQueryArgs
class ServeFileQueryArgs(BaseModel):
    path: str = Field(..., description="The path to the file")


class UpdateTranscriptionRequest(BaseModel):
    id: int = Field(..., description="The id of the transcription")
    crowd: bool = Field(..., description="Whether the audio is a crowd")
    has_music: bool = Field(..., description="Whether the audio has music")
    multispeaker: bool = Field(..., description="Whether the audio is a multispeaker")
    new_text_rating: int = Field(..., description="The new text rating")
    old_text_rating: int = Field(..., description="The old text rating")
    clean_text: str = Field(..., description="The cleaned text")
    cleaned: bool = Field(..., description="Whether the transcription has been cleaned")


# region Transcription Model
class Transcription(Base):
    __tablename__ = 'transcriptions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    path = Column(String, nullable=False, unique=True)
    transcript = Column(String, nullable=False)
    has_music = Column(Boolean, nullable=False)
    multispeaker = Column(Boolean, nullable=False)
    crowd = Column(Boolean, nullable=False)
    last_edited_by = Column(String, nullable=True)
    last_edited_at = Column(DateTime, nullable=True)
    language = Column(String, nullable=False)
    clean_text = Column(String, nullable=False)
    old_text_rating = Column(Integer, nullable=False)
    new_text_rating = Column(Integer, nullable=False)
    cleaned = Column(Boolean, nullable=False)
    def __init__(self, path, transcript, has_music, multispeaker, crowd, last_edited_by, last_edited_at, language, clean_text, old_text_rating, new_text_rating, cleaned):
        self.path = path
        self.transcript = transcript
        self.has_music = has_music
        self.multispeaker = multispeaker
        self.crowd = crowd
        self.last_edited_by = last_edited_by
        self.last_edited_at = last_edited_at
        self.language = language
        self.clean_text = clean_text
        self.old_text_rating = old_text_rating
        self.new_text_rating = new_text_rating
        self.cleaned = cleaned
    def __repr__(self):
        return f"Transcription(path={self.path}, transcript={self.transcript}, has_music={self.has_music}, multispeaker={self.multispeaker}, crowd={self.crowd}, last_edited_by={self.last_edited_by}, last_edited_at={self.last_edited_at})"
    
    def to_dict(self):
        return {
            'id': self.id,
            'path': self.path,
            'transcript': self.transcript,
            'has_music': self.has_music,
            'multispeaker': self.multispeaker,
            'crowd': self.crowd,
            'last_edited_by': self.last_edited_by,
            'last_edited_at': self.last_edited_at,
            'language': self.language,
            'clean_text': self.clean_text,
            'old_text_rating': self.old_text_rating,
            'new_text_rating': self.new_text_rating,
            'cleaned': self.cleaned
        }



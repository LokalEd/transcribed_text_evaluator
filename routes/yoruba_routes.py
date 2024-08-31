from msilib.schema import File
from quart import Blueprint, send_file
from quart_schema import validate_querystring, validate_response
import os
from models.base import get_session, ErrorResponse
from models.yoruba_models import GetTranscriptionQueryArgs, PaginatedTranscriptionResponse, ServeFileQueryArgs
from services.yoruba_services import TranscriptionService

yoruba_routes = Blueprint('yoruba', __name__, url_prefix='/yoruba')

@yoruba_routes.route('/')
async def index():
    return 'Hello, World!'

@yoruba_routes.route('/transcriptions')
@validate_response(PaginatedTranscriptionResponse, status_code=200)
@validate_querystring(GetTranscriptionQueryArgs)
@validate_response(ErrorResponse, status_code=404)
async def transcriptions(query_args: GetTranscriptionQueryArgs):
    page = query_args.page
    per_page = query_args.per_page
    async with get_session() as session:
        service = TranscriptionService(session)
        yoruba_transcriptions, total = await service.get_paginated_transcriptions(page, per_page)
        if not yoruba_transcriptions:
            return ErrorResponse(message="No transcriptions found", status_code=404)
        response = {
            "data": yoruba_transcriptions,
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": (total + per_page - 1) // per_page
        }
        print(response)
        return PaginatedTranscriptionResponse(**response), 200
    

@yoruba_routes.route('/serve_file')
@validate_querystring(ServeFileQueryArgs)
@validate_response(ErrorResponse, status_code=404)
async def serve_file(query_args: ServeFileQueryArgs):
    file_path = os.path.join(os.getcwd(), query_args.path)
    if not os.path.exists(file_path):
        return ErrorResponse(detail=f"File not found: {file_path}", status_code=404)
    return await send_file(file_path)


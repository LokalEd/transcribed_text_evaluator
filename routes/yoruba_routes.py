import logging
import os

from quart import Blueprint, render_template, send_file, url_for
from quart_schema import validate_querystring, validate_request, validate_response

from models.base import BaseResponse, ErrorResponse, get_session
from models.yoruba_models import (
    GetTranscriptionQueryArgs,
    PaginatedTranscriptionResponse,
    ServeFileQueryArgs,
    UpdateTranscriptionRequest,
)
from services.yoruba_services import TranscriptionService

logger = logging.getLogger("hypercorn")

yoruba_routes = Blueprint("yoruba", __name__, url_prefix="/yoruba")


@yoruba_routes.route("/home")
async def index():
    return await render_template("yoruba_index.html")


@yoruba_routes.route("/transcriptions")
@validate_response(PaginatedTranscriptionResponse, status_code=200)
@validate_querystring(GetTranscriptionQueryArgs)
@validate_response(ErrorResponse, status_code=404)
async def transcriptions(query_args: GetTranscriptionQueryArgs):
    page = query_args.page
    per_page = query_args.per_page
    async with get_session() as session:
        service = TranscriptionService(session)
        yoruba_transcriptions, total = await service.get_paginated_transcriptions(
            page, per_page
        )
        if not yoruba_transcriptions:
            return ErrorResponse(message="No transcriptions found", status_code=404)
        for transcription in yoruba_transcriptions:
            transcription["audio_url"] = url_for(
                "yoruba.serve_file", path=transcription["path"], _external=True
            )
        response = {
            "data": yoruba_transcriptions,
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": (total + per_page - 1) // per_page,
        }
        logger.info(response)
        return PaginatedTranscriptionResponse(**response), 200


@yoruba_routes.route("/serve_file")
@validate_querystring(ServeFileQueryArgs)
@validate_response(ErrorResponse, status_code=404)
async def serve_file(query_args: ServeFileQueryArgs):
    file_path = os.path.join(os.getcwd(), query_args.path)
    logger.info(file_path)
    if not os.path.exists(file_path):
        return ErrorResponse(detail=f"File not found: {file_path}", status_code=404)
    return await send_file(file_path)


@yoruba_routes.route("/update_transcription", methods=["POST"])
@validate_request(UpdateTranscriptionRequest)
@validate_response(BaseResponse, status_code=200)
@validate_response(ErrorResponse, status_code=404)
async def update_transcription(data: UpdateTranscriptionRequest):
    logger.info(data)
    async with get_session() as session:
        id_ = data.id
        service = TranscriptionService(session)
        updated, message = await service.update_transcription(id_, data)
    if updated:
        return BaseResponse(message=message), 200
    else:
        return ErrorResponse(detail=message), 404

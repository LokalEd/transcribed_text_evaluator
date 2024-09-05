import uuid

from itsdangerous import BadSignature, SignatureExpired
from quart import Quart, jsonify, request
from quart_schema import (
    QuartSchema,
    RequestSchemaValidationError,
    ResponseSchemaValidationError,
)
from quart_schema.validation import QuerystringValidationError

from models.base import ErrorResponse, init_db, load_data
from routes.yoruba_routes import yoruba_routes

app = Quart("Lokal ED Data API")
QuartSchema(app)
app.config["TEMPLATES_AUTO_RELOAD"] = True

app.register_blueprint(yoruba_routes)
print(app.config.items())


@app.before_serving
async def startup():
    await init_db()
    await load_data()


@app.errorhandler(404)
async def page_not_found(e):
    return jsonify(error=str(e)), 404


@app.errorhandler(RequestSchemaValidationError)
@app.errorhandler(ResponseSchemaValidationError)
@app.errorhandler(QuerystringValidationError)
async def validation_error(
    error: RequestSchemaValidationError | ResponseSchemaValidationError,
):
    # logger.error(error)
    return ErrorResponse(detail=str(error.validation_error)), 400


@app.errorhandler(BadSignature)
async def bad_signature_error(error: BadSignature):
    return ErrorResponse(
        detail=str(error),
    ), 400


@app.errorhandler(SignatureExpired)
async def signature_expired_error(error: SignatureExpired):
    return ErrorResponse(
        detail=str(error),
    ), 400


@app.errorhandler(Exception)
async def exception_handler_route(e: Exception):
    error_id = str(uuid.uuid4())  # noqa: F821
    # logger.error(f"{error_id} - {str(e)}")
    return ErrorResponse(
        detail=f"A server error has occured, please contact support: {error_id} -> {str(e)}"
    ), 500


if __name__ == "__main__":
    app.run()

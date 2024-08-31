
from quart import Quart, jsonify
from quart_schema import QuartSchema

from models.base import init_db, load_data
from routes.yoruba_routes import yoruba_routes

app = Quart("Lokal ED Data API")
QuartSchema(app)

app.register_blueprint(yoruba_routes)

@app.before_serving
async def startup():
    await init_db()
    await load_data()

@app.errorhandler(404)
async def page_not_found(e):
    return jsonify(error=str(e)), 404


@app.errorhandler(500)
async def internal_server_error(e):
    return jsonify(error=str(e)), 500


if __name__ == "__main__":
    app.run()

from sanic import Sanic, Blueprint
from tortoise.contrib.sanic import register_tortoise
from handlers import api
import settings

app = Sanic(__name__)
app.blueprint(api)

register_tortoise(
    app,
    db_url=settings.DATABASE_URI,
    modules={"models": ["database.models", "aerich.models"]},
    generate_schemas=True
)

if __name__ == "__main__":
    app.run(debug=True)
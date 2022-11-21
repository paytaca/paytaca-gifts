from sanic import Sanic, Blueprint
from sanic_ext import Extend
from tortoise.contrib.sanic import register_tortoise
from handlers import api
import settings

app = Sanic(__name__)
app.blueprint(api)
app.config.CORS_ORIGINS = "*"
Extend(app)


TORTOISE_ORM = {
    'connections': {
        'default': settings.DATABASE_URI
    },
    'apps': {
        'models': {"models": ["database.models", "aerich.models"]}
    }
}

register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True
)

if __name__ == "__main__":
    app.run(debug=True)

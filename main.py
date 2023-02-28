from sanic import Sanic, Blueprint, Request
from sanic_ext import Extend, render
from tortoise.contrib.sanic import register_tortoise
from handlers import api
import settings
import os

app = Sanic(__name__)

app_association_blueprint = Blueprint('app-site-association', url_prefix='')
app_association_blueprint.static('/.well-known/apple-app-site-association', './apple-app-site-association.json', name='app-site-association')
app_association_blueprint.static('/.well-known/assetlinks.json', './assetlinks.json', name='assetlinks')

app.blueprint(api)
app.blueprint(app_association_blueprint)
app.config.CORS_ORIGINS = "*"
Extend(app)

current_directory = os.path.dirname(os.path.realpath(__file__))
static_directory = os.path.join(current_directory, 'static')
app.static('/static', static_directory, strict_slashes=False)

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


# HTML pages

@app.get("/claim")
async def handler(request: Request):
    context = {
        "code": request.args.get('code'),
        "title": "You received a BCH gift!",
        "description": "This link delivers a Bitcoin Cash (BCH) gift you can claim using the Paytaca wallet app."
    }
    return await render(
        "gift.html", context=context, status=200
    )


if __name__ == "__main__":
    app.run(debug=True)

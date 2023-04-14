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
from database import models
import hashlib


def generate_gift_code_hash(gift_code):
    return hashlib.sha256(gift_code.encode()).hexdigest()


@app.get("/claim")
async def handler(request: Request):
    gift_code = request.args.get('code')
    gift_code_hash = generate_gift_code_hash(gift_code)
    gift = await models.Gift.filter(gift_code_hash=gift_code_hash).first()
    exists = False
    amount = None
    claimed = False
    if gift:
        exists = True
        amount = float(gift.amount)
        if gift.date_claimed:
            claimed = True

    context = {
        "code": gift_code,
        "exists": exists,
        "amount": amount,
        "claimed": claimed,
        "title": f"This link delivers {amount} BCH gift!",
        "description": "This link delivers a Bitcoin Cash (BCH) gift you can claim using the Paytaca wallet app."
    }
    return await render(
        "gift.html", context=context, status=200
    )


if __name__ == "__main__":
    app.run(debug=True)

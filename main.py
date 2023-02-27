from sanic import Sanic, Blueprint
from sanic_ext import Extend
from tortoise.contrib.sanic import register_tortoise
from handlers import api
import settings

app = Sanic(__name__)

app_association_blueprint = Blueprint('app-site-association', url_prefix='')
app_association_blueprint.static('/.well-known/apple-app-site-association', './apple-app-site-association.json', name='app-site-association')
app_association_blueprint.static('/.well-known/assetlinks.json', './assetlinks.json', name='assetlinks')

app.blueprint(api)
app.blueprint(app_association_blueprint)
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

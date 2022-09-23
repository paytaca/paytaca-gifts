from sanic import Blueprint
from .campaigns import campaigns
from .gifts import gifts

api = Blueprint.group(campaigns, gifts, url_prefix="/api")

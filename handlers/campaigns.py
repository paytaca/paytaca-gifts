# from sanic.exceptions import SanicException
from sanic.blueprints import Blueprint
from sanic.response import json
from sanic_ext import openapi
from sanic_ext.extensions.openapi.definitions import Parameter, Response, RequestBody
# from sanic.log import logger
from uuid import UUID

from utils import doc_schemas
from database import models

campaigns = Blueprint('Campaigns', '/campaigns')

@campaigns.get("/<wallet_hash:str>/list", strict_slashes=False)
@openapi.definition(
    summary="Fetches a list of Campaigns filtered by wallet hash with pagination.",
    parameter=[
        Parameter("offset", int, "query"),
        Parameter("limit", int, "query")
    ],
    response=[
        Response(status=200, content={"application/json": doc_schemas.ListCampaignsResponse}, description="Returns a list of Campaign objects")
    ]
)
async def list_campaigns(request, wallet_hash: str):
    """Fetches a list of Campaigns filtered by wallet hash with pagination"""
    offset = 0 
    limit = 0
    query_args = request.args

    if query_args.get("offset"):
        offset = int(query_args.get("offset"))
    
    if query_args.get("limit"):
        limit = int(query_args.get("limit"))
    
    query_resp = await models.Campaign.filter(wallet__wallet_hash=wallet_hash).offset(offset).limit(limit)

    campaigns = []
    for campaign in query_resp:
        await campaign.fetch_related('gifts')
        await campaign.fetch_related('claims')
        campaigns.append({
            "id": str(campaign.id),
            "date_created": str(campaign.date_created),
            "name": campaign.name,
            "limit_per_wallet": campaign.limit_per_wallet,
            "gifts": len(campaign.gifts),
            "claims": len(campaign.claims)
        })

    return json({"campaigns": campaigns})

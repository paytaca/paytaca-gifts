# from sanic.exceptions import SanicException
from sanic.blueprints import Blueprint
from sanic.response import json
from sanic_ext import openapi
from sanic_ext.extensions.openapi.definitions import Parameter, Response, RequestBody
from uuid import UUID

from utils import doc_schemas
from database import models

campaigns = Blueprint('Campaigns', '/campaigns')

@campaigns.get("/list", strict_slashes=False)
@openapi.definition(
    summary="Fetches a list of Campaigns filtered by wallet hash with pagination.",
    parameter=[
        Parameter("offset", int, "query"),
        Parameter("limit", int, "query"),
        Parameter("wallet_hash", str, "query"),
    ],
    response=[
        Response(status=200, content={"application/json": doc_schemas.ListCampaignsResponse}, description="Returns a list of Campaign objects")
    ]
)
async def list_campaigns(request):
    """Fetches a list of Campaigns filtered by wallet hash with pagination"""
    offset = 0 
    limit = 0
    query_args = request.args

    if query_args.get("offset"):
        offset = int(query_args.get("offset"))
    
    if query_args.get("limit"):
        limit = int(query_args.get("limit"))
    
    query_resp = None
    if query_args.get("wallet_hash"):
        query_resp = await models.Campaign.filter(gifts__claims__wallet_hash=query_args.get("wallet_hash")).offset(offset).limit(limit)
    else:
        query_resp = await models.Campaign.all().offset(offset).limit(limit)

    campaigns = []
    for campaign in query_resp:
        campaigns.append({
            "id": str(campaign.id),
            "name": campaign.name,
            "limit_per_wallet": campaign.limit_per_wallet,
        })

    return json({"campaigns": campaigns})

# @openapi.definition(
#     summary="Creates a Campaign.",
#     body=RequestBody({"application/json": doc_schemas.CreateCampaignPayload}, required=True),
#     response=[
#         Response(status=200, content={"application/json": doc_schemas.CreateCampaignResponse}, description="Returns a list of Campaign objects")
#     ]
# )
# @campaigns.post("/create", strict_slashes=False)
# async def create_campaign(request):
#     """Creates a new Campaign record"""
#     try:
#         limit_per_wallet = request.json["limit_per_wallet"]
#     except:
#         raise SanicException("Limit per wallet required", status_code=400)

#     campaign = await Campaign.create(limit_per_wallet=limit_per_wallet)
#     return json({"campaign": str(campaign)})
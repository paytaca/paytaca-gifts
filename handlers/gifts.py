from sanic.exceptions import SanicException
from sanic.blueprints import Blueprint
from sanic.response import json
from sanic_ext import openapi, validate
from sanic_ext.extensions.openapi.definitions import Parameter, Response, RequestBody
from sanic_validation import validate_json
from uuid import UUID

from utils import doc_schemas
from database import models
from tortoise.functions import Sum

gifts = Blueprint('Gifts', '/gifts')

@gifts.get("/list", strict_slashes=False)
@openapi.definition(
    summary="Fetches a list of Gifts filtered by wallet hash with pagination.",
    parameter=[
        Parameter("offset", int, "query"),
        Parameter("limit", int, "query"),
        Parameter("wallet_hash", str, "query"),
    ],
    response=[
        Response(status=200, content={"application/json": doc_schemas.ListGiftsResponse}, description="Returns a list of Gift objects")
    ]
)
async def list_gifts(request):
    offset = 0 
    limit = 0
    query_args = request.args

    if query_args.get("offset"):
        offset = int(query_args.get("offset"))
    
    if query_args.get("limit"):
        limit = int(query_args.get("limit"))
    
    query_resp = []
    if query_args.get("wallet_hash"):
        query_resp = await models.Gift.filter(claims__wallet_hash=query_args.get("wallet_hash")).offset(offset).limit(limit)
    else:
        query_resp = await models.Gift.all().offset(offset).limit(limit)

    gifts = []
    for gift in query_resp:
        await gift.fetch_related("campaign")
        campaign = gift.campaign
        gifts.append({
            "gift_id": str(gift.gift_id),
            "amount": gift.amount,
            "campaign_id": str(campaign)
        })

    return json({"gifts": gifts})


@gifts.post("/create", strict_slashes=False)
@openapi.definition(
    summary="Creates a Gift record. Creates a Campaign record if `limit_per_wallet` is not null.",
    body=RequestBody({"application/json": doc_schemas.CreateGiftPayload}, required=True),
    response=[
        Response(status=200, content={"application/json": doc_schemas.CreateGiftResponse}, description="Returns the id of the created Gift record")
    ]
)
@validate_json(
    {
        "gift_id": { "type": "string", "required": True },
        "share": { "type": "string", "required": True },
        "amount": { "type": "float", "required": True },
        "campaign": { "type": "dict", "required": False }
    }
)
async def create_gift(request):
    data = request.json
    if "campaign" in data:
        if "limit_per_wallet" in data["campaign"]:
            limit = data["campaign"]["limit_per_wallet"]
            name = data["campaign"]["name"]
            campaign = await models.Campaign.create(name=name, limit_per_wallet=limit)
        elif "id" in data["campaign"]:
            campaign = await models.Campaign.get(data["campaign"]["id"])
    else:
        campaign = None
    
    gift = await models.Gift.create(
        gift_id=data["gift_id"],
        amount=data["amount"],
        share=data["share"],
        campaign=campaign
    )
    return json({"gift": str(gift)})


@gifts.post("/<gift_id:str>/claim", strict_slashes=False)
@openapi.definition(
    summary="Claim a Gift record.",
    body=RequestBody({"application/json": doc_schemas.ClaimGiftPayload}, required=True),
    response=[
        Response(status=200, content={"application/json": doc_schemas.ClaimGiftResponse}, description="Returns the id of the Claim record.")
    ]
)
async def claim_gift(request, gift_id: str):
    wallet_hash = request.json["wallet_hash"]
    gift = await models.Gift.filter(gift_id=gift_id).first()
    
    if gift is None:
        raise SanicException(
            "Gift does not exist!", 
            status_code=400
        )
    
    claims_sum = None
    if gift.campaign:
        result = await gift.campaign.claims.filter(wallet_hash=wallet_hash).annotate(
            claims=Sum('amount')
        )
        claims_sum = result['claims__sum'] or 0

    if claims_sum >= gift.campaign.limit_per_wallet:
        raise SanicException(
            "You have exceeded the limit of gifts to claim for this campaign", 
            status_code=409
        )
    
    claim = await models.Claim.create(wallet_hash=wallet_hash, gift=gift)
    return json({
        "share": gift.share
    })

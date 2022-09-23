from sanic.exceptions import SanicException
from sanic.blueprints import Blueprint
from sanic.response import json
from sanic_ext import openapi
from sanic_ext.extensions.openapi.definitions import Parameter, Response, RequestBody
from uuid import UUID

from utils import doc_schemas
import models

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
            "id": str(gift.id),
            "share": gift.share,
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
async def create_gift(request):
    try:
        share = request.json["share"]
    except:
        raise SanicException("Gift share is required", status_code=400)
   
    campaign = None
    if "limit_per_wallet" in request.json and request.json["limit_per_wallet"]:
        campaign = await models.Campaign.create(limit_per_wallet=request.json["limit_per_wallet"])
    
    gift = await models.Gift.create(share=share, campaign=campaign)
    return json({"gift": str(gift)})


@gifts.post("/<gift_id:uuid>/claim", strict_slashes=False)
@openapi.definition(
    summary="Claim a Gift record.",
    body=RequestBody({"application/json": doc_schemas.ClaimGiftPayload}, required=True),
    response=[
        Response(status=200, content={"application/json": doc_schemas.ClaimGiftResponse}, description="Returns the id of the Claim record.")
    ]
)
async def claim_gift(request, gift_id: UUID):
    wallet_hash = request.json["wallet_hash"]
    gift = await models.Gift.filter(pk=gift_id).first()
    
    if gift is None:
        raise SanicException(
            "Gift does not exist!", 
            status_code=400
        )
    
    claim_count = await models.Claim.filter(wallet_hash=wallet_hash, gift=gift).count()

    if claim_count > 0:
        raise SanicException(
            "Gift already claimed by this wallet", 
            status_code=400
        )
    
    claim = await models.Claim.create(wallet_hash=wallet_hash, gift=gift)
    return json({
        "claim": str(claim)
    })
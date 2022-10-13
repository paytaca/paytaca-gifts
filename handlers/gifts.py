from sanic.exceptions import SanicException
from sanic.blueprints import Blueprint
from sanic.response import json
from sanic_ext import openapi, validate
from sanic_ext.extensions.openapi.definitions import Parameter, Response, RequestBody
from sanic_validation import validate_json
# from sanic.log import logger
from uuid import UUID
from datetime import datetime

from utils import doc_schemas
from database import models
from tortoise.functions import Sum

gifts = Blueprint('Gifts', '/gifts')

@gifts.get("/<wallet_hash:str>/list", strict_slashes=False)
@openapi.definition(
    summary="Fetches a list of Gifts filtered by wallet hash with pagination.",
    parameter=[
        Parameter("offset", int, "query"),
        Parameter("limit", int, "query")
    ],
    response=[
        Response(status=200, content={"application/json": doc_schemas.ListGiftsResponse}, description="Returns a list of Gift objects")
    ]
)
async def list_gifts(request, wallet_hash: str):
    offset = 0 
    limit = 0
    query_args = request.args

    if query_args.get("offset"):
        offset = int(query_args.get("offset"))
    
    if query_args.get("limit"):
        limit = int(query_args.get("limit"))
    
    query_resp = await models.Gift.filter(wallet__wallet_hash=wallet_hash).offset(offset).limit(limit)

    gifts = []
    for gift in query_resp:
        await gift.fetch_related("campaign")
        campaign = gift.campaign
        gifts.append({
            "gift_code_hash": str(gift.gift_code_hash),
            "date_created": str(gift.date_created),
            "amount": gift.amount,
            "campaign_id": str(campaign),
            "date_claimed": str(gift.date_claimed)
        })

    return json({"gifts": gifts})


@gifts.post("/<wallet_hash:str>/create", strict_slashes=False)
@openapi.definition(
    summary="Creates a Gift record. Creates a Campaign record if `limit_per_wallet` is not null.",
    body=RequestBody({"application/json": doc_schemas.CreateGiftPayload}, required=True),
    response=[
        Response(status=200, content={"application/json": doc_schemas.CreateGiftResponse}, description="Returns the id of the created Gift record")
    ]
)
@validate_json(
    {
        "gift_code_hash": { "type": "string", "required": True },
        "share": { "type": "string", "required": True },
        "address": { "type": "string", "required": True },
        "amount": { "type": "float", "required": True },
        "campaign": { "type": "dict", "required": False }
    }
)
async def create_gift(request, wallet_hash: str):
    data = request.json
    wallet, _ = await models.Wallet.get_or_create(wallet_hash=wallet_hash)
    if "campaign" in data:
        if "limit_per_wallet" in data["campaign"]:
            limit = data["campaign"]["limit_per_wallet"]
            name = data["campaign"]["name"]
            campaign = await models.Campaign.create(name=name, wallet=wallet, limit_per_wallet=limit)
        elif "id" in data["campaign"]:
            campaign = await models.Campaign.get(id=data["campaign"]["id"])
    else:
        campaign = None
    
    gift = await models.Gift.create(
        gift_code_hash=data["gift_code_hash"],
        address=data["address"],
        wallet=wallet,
        amount=data["amount"],
        share=data["share"],
        campaign=campaign
    )
    return json({"gift": str(gift)})


@gifts.post("/<gift_code_hash:str>/claim", strict_slashes=False)
@openapi.definition(
    summary="Claim a Gift record.",
    body=RequestBody({"application/json": doc_schemas.ClaimGiftPayload}, required=True),
    response=[
        Response(status=200, content={"application/json": doc_schemas.ClaimGiftResponse}, description="Returns the id of the Claim record.")
    ]
)
async def claim_gift(request, gift_code_hash: str):
    wallet_hash = request.json["wallet_hash"]
    wallet, _ = await models.Wallet.get_or_create(wallet_hash=wallet_hash)
    gift = await models.Gift.filter(gift_code_hash=gift_code_hash).first()
    if gift is None:
        raise SanicException(
            "Gift does not exist!", 
            status_code=400
        )

    claim = await models.Claim.filter(gift=gift.id, wallet=wallet).first()
    if claim:
        return json({
            "share": gift.share,
            "claim_id": str(claim.id)
        })

    await gift.fetch_related('campaign')
    if gift.campaign:
        await gift.campaign.fetch_related('claims')
        claims = gift.campaign.claims
        claims_sum = 0
        if len(claims) > 0:
            result = await models.Claim.filter(
                campaign=gift.campaign,
                wallet_hash=wallet_hash
            ).annotate(
                claims_sum=Sum("amount")
            ).values('claims_sum')
            claims_sum = result[0]['claims_sum']
        if claims_sum < gift.campaign.limit_per_wallet:
            claim = await models.Claim.create(
                wallet=wallet,
                amount=gift.amount,
                gift=gift,
                campaign=gift.campaign
            )
        else:
            raise SanicException(
                "You have exceeded the limit of gifts to claim for this campaign", 
                status_code=409
            )
    else:
        claim = await models.Claim.create(
            wallet=wallet,
            amount=gift.amount,
            gift=gift
        )

    if claim:
        await models.Gift.filter(id=gift.id).update(date_claimed=datetime.now())
        return json({
            "share": gift.share,
            "claim_id": str(claim.id)
        })
    else:
        raise SanicException(
            "This gift has been claimed", 
            status_code=409
        )

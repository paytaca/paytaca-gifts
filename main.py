import logging

from models import Campaign, Gift, Claim
from sanic import Sanic, response, text
from sanic.exceptions import SanicException
from uuid import UUID
from tortoise.contrib.sanic import register_tortoise

# logging.basicConfig(level=logging.DEBUG)

from sanic_openapi import swagger_blueprint
from sanic_openapi import openapi2_blueprint

app = Sanic(__name__)

app.blueprint(swagger_blueprint)
app.blueprint(openapi2_blueprint)

@app.route("/campaigns/list", methods=["GET"])
async def list_campaigns(request):

    offset = 0 
    limit = 0
    query_args = request.args

    if query_args.get("offset"):
        offset = int(query_args.get("offset"))
    
    if query_args.get("limit"):
        limit = int(query_args.get("limit"))
    
    query_resp = None
    if query_args.get("wallet_hash"):
        query_resp = await Campaign.filter(gifts__claims__wallet_hash=query_args.get("wallet_hash")).offset(offset).limit(limit)
    else:
        query_resp = await Campaign.all().offset(offset).limit(limit)

    campaigns = []
    for campaign in query_resp:
        campaigns.append({
            "id": str(campaign.id),
            "limit_per_wallet": campaign.limit_per_wallet,
        })

    return response.json({"campaigns": campaigns})

@app.route("/gifts/list", methods=["GET"])
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
        query_resp = await Gift.filter(claims__wallet_hash=query_args.get("wallet_hash")).offset(offset).limit(limit)
    else:
        query_resp = await Gift.all().offset(offset).limit(limit)

    gifts = []
    for gift in query_resp:
        await gift.fetch_related("campaign")
        campaign = gift.campaign
        gifts.append({
            "id": str(gift.id),
            "share": gift.share,
            "campaign_id": str(campaign)
        })

    return response.json({"gifts": gifts})

@app.route("/campaigns/create", methods=["POST"])
async def create_campaign(request):
    try:
        limit_per_wallet = request.json["limit_per_wallet"]
    except:
        raise SanicException("Limit per wallet required", status_code=400)

    campaign = await Campaign.create(limit_per_wallet=limit_per_wallet)
    return response.json({"campaign": str(campaign)})

@app.route("/gifts/create", methods=["POST"])
async def create_gift(request):
    try:
        share = request.json["share"]
    except:
        raise SanicException("Gift share is required", status_code=400)
   
    campaign = None
    if "limit_per_wallet" in request.json:
        campaign = await Campaign.create(limit_per_wallet=request.json["limit_per_wallet"])
    
    gift = await Gift.create(share=share, campaign=campaign)
    return response.json({"gift": str(gift)})

@app.route("/gifts/<gift_id:uuid>/claim", methods=["POST"])
async def claim_gift(request, gift_id: UUID):
    wallet_hash = request.json["wallet_hash"]
    gift = await Gift.filter(pk=gift_id).first()
    if gift is None:
        raise SanicException("Gift does not exist!", status_code=400)
    
    claim = await Claim.filter(wallet_hash=wallet_hash, gift=gift)
    if len(claim) > 0:
        raise SanicException("Gift already claimed by this wallet", status_code=400)
    
    claim = await Claim.create(wallet_hash=wallet_hash, gift=gift)
    
    return response.json({
        "claim": str(claim)
    })
    

register_tortoise(
    app, db_url="sqlite://:memory:", modules={"models": ["models"]}, generate_schemas=True
)

if __name__ == "__main__":
    app.run(debug=True)
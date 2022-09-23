import logging

from models import Campaign, Gift
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

# @app.route("/gifts/<gift_id:uuid>/claim")
# async def claim_gift(request, gift_id: UUID):
#     # wallet hash must not have already claimed from this gift
#     # sh
#     pass

register_tortoise(
    app, db_url="sqlite://:memory:", modules={"models": ["models"]}, generate_schemas=True
)

if __name__ == "__main__":
    app.run(debug=True)
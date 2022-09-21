import logging

from models import Campaigns, Gifts
from sanic import Sanic, response
from sanic.exceptions import SanicException

from tortoise.contrib.sanic import register_tortoise

logging.basicConfig(level=logging.DEBUG)

app = Sanic(__name__)

@app.get("/campaigns/list")
async def list_campaigns(request):
    campaigns = await Campaigns.all()
    return response.json({"campaigns": [str(campaign) for campaign in campaigns]})

@app.post("/campaigns/create")
async def create_campaign(request):
    try:
        limit_per_wallet = request.json["limit_per_wallet"]
    except:
        raise SanicException("Limit per wallet required", status_code=400)

    campaign = await Campaigns.create(limit_per_wallet=limit_per_wallet)
    return response.json({"campaign": str(campaign)})

@app.get("/gifts/list")
async def list_gifts(request):
    gifts = await Gifts.all()
    return response.json({"gifts": [str(gift) for gift in gifts]})

@app.post("/gifts/create")
async def create_gift(request):
    try:
        share = request.json["share"]
    except:
        raise SanicException("Gift share is required", status_code=400)
    
    campaign = None
    if request.json.has_key("limit_per_wallet"):
        campaign = await Campaigns.create(limit_per_wallet=limit_per_wallet)
    
    gift = await Gifts.create(share=share, campaign=campaign)
    return response.json({"gift": str(gift)})

@app.post("/gift/<gift_id:uuid>/claim")
async def claim_gift(request):
    pass

register_tortoise(
    app, db_url="sqlite://:memory:", modules={"models": ["models"]}, generate_schemas=True
)

if __name__ == "__main__":
    app.run(debug=True)
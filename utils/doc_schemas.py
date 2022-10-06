#### payloads
class CreateGiftPayload:
    gift_id: str
    share: str
    amount: float
    limit_per_wallet: int

class ClaimGiftPayload:
    wallet_hash: str

#### responses
class CreateGiftResponse:
    gift: str

class ClaimGiftResponse:
    share: str

class ListGiftsResponse:
    gifts: [{}]

class ListCampaignsResponse:
    response: [{}]
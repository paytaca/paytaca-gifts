#### payloads
class CreateGiftPayload:
    gift_code_hash: str
    address: str
    share: str
    amount: float
    campaign: {}

class ClaimGiftPayload:
    wallet_hash: str

#### responses
class CreateGiftResponse:
    gift: str

class ClaimGiftResponse:
    share: str
    claim_id: str

class ListGiftsResponse:
    gifts: [{}]

class ListCampaignsResponse:
    response: [{}]
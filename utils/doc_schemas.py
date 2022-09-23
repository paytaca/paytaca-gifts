#### payloads
class CreateGiftPayload:
    share: int
    limit_per_wallet: int

class ClaimGiftPayload:
    wallet_hash: str

#### responses
class CreateGiftResponse:
    gift: str

class ClaimGiftResponse:
    claim: str

class ListGiftsResponse:
    gifts: [{}]

class ListCampaignsResponse:
    response: [{}]
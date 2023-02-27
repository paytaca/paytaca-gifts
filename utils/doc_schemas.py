import typing
from datetime import datetime

#### payloads
class LimitOffsetPaginationInfo:
    count: int
    limit: int
    offset: int

class GiftPayload:
    gift_code_hash: str
    date_created: datetime
    amount: float
    campaign_id: str
    date_claimed: datetime

class CampaignPayload:
    id: str
    date_created: datetime
    name: str
    limit_per_wallet: float
    gifts: int
    claims: int    

class CreateGiftPayload:
    gift_code_hash: str
    address: str
    share: str
    amount: float
    campaign: {}

class ClaimGiftPayload:
    wallet_hash: str

class RecoverGiftPayload:
    wallet_hash: str

#### responses
class CreateGiftResponse:
    gift: str

class ClaimGiftResponse:
    share: str
    claim_id: str

class RecoverGiftResponse:
    share: str

class ListGiftsResponse:
    gifts: [GiftPayload]
    pagination: LimitOffsetPaginationInfo

class ListCampaignsResponse:
    campaigns: [CampaignPayload]
    pagination: LimitOffsetPaginationInfo

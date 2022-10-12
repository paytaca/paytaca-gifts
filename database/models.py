from tortoise import fields
from tortoise.models import Model

class Campaign(Model):
    id = fields.UUIDField(pk=True)
    date_created = fields.DatetimeField(auto_now_add=True)
    name = fields.CharField(max_length=50)
    limit_per_wallet = fields.FloatField()

    gifts: fields.ReverseRelation["Gift"]
    claims: fields.ReverseRelation["Claim"]

    def __str__(self):
        return str(self.id)

class Gift(Model):
    id = fields.UUIDField(pk=True)
    date_created = fields.DatetimeField(auto_now_add=True)
    gift_id = fields.CharField(max_length=70, index=True, unique=True)
    amount = fields.FloatField(default=0)
    share = fields.CharField(max_length=255)
    date_claimed = fields.DatetimeField(null=True)

    campaign: fields.ForeignKeyRelation[Campaign] = fields.ForeignKeyField(
        "models.Campaign", related_name="gifts", to_field="id", null=True
    )
    claims: fields.ReverseRelation["claim"]

    def __str__(self):
        return str(self.id)

class Claim(Model):
    id = fields.UUIDField(pk=True)
    date_created = fields.DatetimeField(auto_now_add=True)
    wallet_hash = fields.CharField(max_length=64)
    amount = fields.FloatField(default=0)

    gift: fields.ForeignKeyRelation[Gift] = fields.ForeignKeyField(
        "models.Gift", related_name="claims", to_field="id"
    )
    campaign: fields.ForeignKeyRelation[Campaign] = fields.ForeignKeyField(
        "models.Campaign", related_name="claims", to_field="id", null=True
    )

    class Meta:
        unique_together = ('wallet_hash', 'gift_id')

    def __str__(self):
        return str(self.id)

from tortoise import fields
from tortoise.models import Model

class Campaign(Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=50)
    limit_per_wallet = fields.FloatField()

    gifts: fields.ReverseRelation["Gift"]
    claims: fields.ReverseRelation["Claim"]

    def __str__(self):
        return str(self.id)

class Gift(Model):
    id = fields.UUIDField(pk=True)
    gift_id = fields.CharField(max_length=70)
    amount = fields.FloatField(default=0)
    share = fields.CharField(max_length=255)

    campaign: fields.ForeignKeyRelation[Campaign] = fields.ForeignKeyField(
        "models.Campaign", related_name="gifts", to_field="id", null=True
    )
    claims: fields.ReverseRelation["claim"]

    def __str__(self):
        return str(self.id)

class Claim(Model):
    id = fields.UUIDField(pk=True)
    wallet_hash = fields.CharField(max_length=64)
    amount = fields.FloatField(default=0)

    gift: fields.ForeignKeyRelation[Gift] = fields.ForeignKeyField(
        "models.Gift", related_name="claims", to_field="id"
    )
    campaign: fields.ForeignKeyRelation[Campaign] = fields.ForeignKeyField(
        "models.Campaign", related_name="claims", to_field="id", null=True
    )

    def __str__(self):
        return str(self.id)

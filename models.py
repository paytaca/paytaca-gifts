from tortoise import fields
from tortoise.models import Model

class Campaign(Model):
    id = fields.UUIDField(pk=True)
    limit_per_wallet = fields.IntField()

    gifts: fields.ReverseRelation["campaign"]

    def __str__(self):
        return str(self.id)

class Gift(Model):
    id = fields.UUIDField(pk=True)
    share = fields.CharField(max_length=255)
    campaign: fields.ForeignKeyRelation[Campaign] = fields.ForeignKeyField(
        "models.Campaign", related_name="gifts", to_field="id", null=True
    )
    wallets: fields.ManyToManyRelation["Wallet"] = fields.ManyToManyField(
        "models.Wallet", related_name="gifts", through="gift_wallet"
    )

    def __str__(self):
        return str(self.id)

class Wallet(Model):
    wallet_hash = fields.CharField(pk=True, max_length=64)
    
    gifts: fields.ManyToManyRelation[Gift]
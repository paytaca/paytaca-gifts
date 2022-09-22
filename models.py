from tortoise import fields
from tortoise.models import Model

class Campaigns(Model):
    id = fields.UUIDField(pk=True)
    limit_per_wallet = fields.IntField()

    gifts: fields.ReverseRelation["campaign"]

    def __str__(self):
        return str(self.id)

class Gifts(Model):
    id = fields.UUIDField(pk=True)
    share = fields.CharField(max_length=255)
    campaign: fields.ForeignKeyRelation[Campaigns] = fields.ForeignKeyField(
        "models.Campaigns", related_name="gifts", to_field="id", null=True
    )

    def __str__(self):
        return str(self.id)
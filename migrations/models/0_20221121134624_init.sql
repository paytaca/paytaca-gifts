-- upgrade --
CREATE TABLE IF NOT EXISTS "wallet" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "date_created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "wallet_hash" VARCHAR(64) NOT NULL
);
CREATE TABLE IF NOT EXISTS "campaign" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "date_created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "name" VARCHAR(50) NOT NULL,
    "limit_per_wallet" DOUBLE PRECISION NOT NULL,
    "wallet_id" UUID NOT NULL REFERENCES "wallet" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "gift" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "date_created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "gift_code_hash" VARCHAR(70) NOT NULL UNIQUE,
    "address" VARCHAR(64) NOT NULL,
    "amount" DOUBLE PRECISION NOT NULL  DEFAULT 0,
    "share" VARCHAR(255) NOT NULL,
    "date_funded" TIMESTAMPTZ,
    "date_claimed" TIMESTAMPTZ,
    "campaign_id" UUID REFERENCES "campaign" ("id") ON DELETE CASCADE,
    "wallet_id" UUID NOT NULL REFERENCES "wallet" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_gift_gift_co_aadf42" ON "gift" ("gift_code_hash");
CREATE TABLE IF NOT EXISTS "claim" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "date_created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "amount" DOUBLE PRECISION NOT NULL  DEFAULT 0,
    "campaign_id" UUID REFERENCES "campaign" ("id") ON DELETE CASCADE,
    "gift_id" UUID NOT NULL REFERENCES "gift" ("id") ON DELETE CASCADE,
    "wallet_id" UUID NOT NULL REFERENCES "wallet" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_claim_wallet__2958f2" UNIQUE ("wallet_id", "gift_id")
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);

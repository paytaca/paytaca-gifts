-- upgrade --
CREATE INDEX "idx_wallet_wallet__7cd411" ON "wallet" ("wallet_hash");
-- downgrade --
DROP INDEX "idx_wallet_wallet__7cd411";

from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "ban" (
    "uid" BIGSERIAL NOT NULL PRIMARY KEY,
    "banned_by" BIGINT,
    "reason" TEXT NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL
);
CREATE TABLE IF NOT EXISTS "user" (
    "uid" BIGSERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(129) NOT NULL,
    "admin" BOOL NOT NULL  DEFAULT False,
    "mute_friend_requests" BOOL NOT NULL  DEFAULT False,
    "autoend" BOOL NOT NULL  DEFAULT True,
    "autoend_time" SMALLINT NOT NULL  DEFAULT 10,
    "created_at" TIMESTAMPTZ NOT NULL
);
CREATE TABLE IF NOT EXISTS "sretsession" (
    "message_id" BIGSERIAL NOT NULL PRIMARY KEY,
    "start" TIMESTAMPTZ NOT NULL,
    "end" TIMESTAMPTZ,
    "autoend" BOOL NOT NULL,
    "sret_type" SMALLINT NOT NULL,
    "user_id" BIGINT NOT NULL REFERENCES "user" ("uid") ON DELETE CASCADE
);
COMMENT ON COLUMN "sretsession"."sret_type" IS 'SRET: 1\nDRISHET: 2\nPERNUL: 3';
CREATE TABLE IF NOT EXISTS "friendrequest" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "message_id" BIGINT,
    "requested_user_id" BIGINT NOT NULL REFERENCES "user" ("uid") ON DELETE CASCADE,
    "user_id" BIGINT NOT NULL REFERENCES "user" ("uid") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "group" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(32) NOT NULL,
    "notify_perdish" BOOL NOT NULL  DEFAULT True,
    "password" INT NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL,
    "owner_id" BIGINT NOT NULL REFERENCES "user" ("uid") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "notify" (
    "message_id" BIGSERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL,
    "scheduled_users_count" INT NOT NULL,
    "executed_users_count" INT NOT NULL  DEFAULT 0,
    "initiated_by_id" BIGINT NOT NULL REFERENCES "user" ("uid") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "apitoken" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "token" VARCHAR(64) NOT NULL UNIQUE,
    "name" VARCHAR(64) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL,
    "valid" BOOL NOT NULL  DEFAULT True,
    "owner_id" BIGINT NOT NULL REFERENCES "user" ("uid") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS "friend_user" (
    "user_rel_id" BIGINT NOT NULL REFERENCES "user" ("uid") ON DELETE CASCADE,
    "user_id" BIGINT NOT NULL REFERENCES "user" ("uid") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "group_member" (
    "group_id" INT NOT NULL REFERENCES "group" ("id") ON DELETE CASCADE,
    "user_id" BIGINT NOT NULL REFERENCES "user" ("uid") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "group_request" (
    "group_id" INT NOT NULL REFERENCES "group" ("id") ON DELETE CASCADE,
    "user_id" BIGINT NOT NULL REFERENCES "user" ("uid") ON DELETE CASCADE
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """

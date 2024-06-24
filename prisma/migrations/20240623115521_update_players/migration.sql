-- DropIndex
DROP INDEX "player_nick_key";

-- AlterTable
ALTER TABLE "player" ALTER COLUMN "nick" SET DEFAULT '';

-- DropForeignKey
ALTER TABLE "team_with_player" DROP CONSTRAINT "team_with_player_playerId_fkey";

-- DropForeignKey
ALTER TABLE "team_with_player" DROP CONSTRAINT "team_with_player_teamId_fkey";

-- AlterTable
ALTER TABLE "team_with_player" ALTER COLUMN "playerId" DROP NOT NULL,
ALTER COLUMN "teamId" DROP NOT NULL;

-- AddForeignKey
ALTER TABLE "team_with_player" ADD CONSTRAINT "team_with_player_playerId_fkey" FOREIGN KEY ("playerId") REFERENCES "player"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "team_with_player" ADD CONSTRAINT "team_with_player_teamId_fkey" FOREIGN KEY ("teamId") REFERENCES "team"("id") ON DELETE SET NULL ON UPDATE CASCADE;

/*
  Warnings:

  - You are about to drop the `team_with_player` table. If the table is not empty, all the data it contains will be lost.

*/
-- DropForeignKey
ALTER TABLE "team_with_player" DROP CONSTRAINT "team_with_player_playerId_fkey";

-- DropForeignKey
ALTER TABLE "team_with_player" DROP CONSTRAINT "team_with_player_teamId_fkey";

-- DropTable
DROP TABLE "team_with_player";

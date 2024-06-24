-- CreateTable
CREATE TABLE "team_with_player" (
    "id" SERIAL NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "playerId" INTEGER,
    "teamId" INTEGER,

    CONSTRAINT "team_with_player_pkey" PRIMARY KEY ("id")
);

-- AddForeignKey
ALTER TABLE "team_with_player" ADD CONSTRAINT "team_with_player_playerId_fkey" FOREIGN KEY ("playerId") REFERENCES "player"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "team_with_player" ADD CONSTRAINT "team_with_player_teamId_fkey" FOREIGN KEY ("teamId") REFERENCES "team"("id") ON DELETE SET NULL ON UPDATE CASCADE;

/*
  Warnings:

  - A unique constraint covering the columns `[name]` on the table `team` will be added. If there are existing duplicate values, this will fail.

*/
-- AlterTable
ALTER TABLE "team" ALTER COLUMN "name" DROP DEFAULT;

-- CreateIndex
CREATE UNIQUE INDEX "team_name_key" ON "team"("name");

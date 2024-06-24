import { PrismaClient } from '@prisma/client'
import { Router } from 'express'
import { join } from 'path'
const router = Router()
const prisma = new PrismaClient()

router.get('/get-all-teams', async (req, res) => {
	try {
		const page = Number(req.query.page) || 1
		const size = Number(req.query.size) || 10

		const skip = (page - 1) * size

		const teams = await prisma.team.findMany({
			skip: skip,
			take: size,
		})

		const totalTeams = await prisma.team.count()

		const totalPages = Math.ceil(totalTeams / size)

		res.status(200).json({
			teams: teams,
			page: page,
			size: size,
			totalTeams: totalTeams,
			totalPages: totalPages,
		})
	} catch (error) {
		res.status(500).json({ error: error.message })
	}
})

router.get('/get-team-logo/:filename', (req, res) => {
	const filename = req.params.filename
	const filePath = join(__dirname, `../../uploads/teams/${filename}`)
	res.sendFile(filePath)
})

export default router

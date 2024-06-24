// seed.js
import { PrismaClient } from '@prisma/client'
import fs from 'fs'

const prisma = new PrismaClient()

async function main() {
	console.log('Start seeding...')

	fs.readFile('./data.json', 'utf8', async (err, data) => {
		if (err) {
			console.error('Ошибка при чтении файла:', err)
			return
		}

		try {
			const jsonData = JSON.parse(data)
			for (const team of jsonData['teams']) {
				await prisma.team.create({
					data: {
						country: team.country_text,
						earned: String(team.earned),
						flagPath: team.flag,
						logoPath: team.org_image,
						name: team.org_name,
						location: team.location,
						worldRating: String(team.world_rating),
						dominateColor: team.org_image_dominant_color,
					},
				})
			}
		} catch (err) {
			console.error('Ошибка при разборе JSON:', err)
		}
	})
	console.log('Seeding finished.')
}

main()
	.catch(e => {
		throw e
	})
	.finally(async () => {
		await prisma.$disconnect()
	})

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
			for (const player of jsonData['players']) {
				await prisma.player.create({
					data: {
						nick: player.player_nick,
						birthDate: player.player_birth_date,
						country: player.player_country_name,
						name: player.player_fullname,
						photoPath: player.player_image_name,
						position: player.player_position_name,
						dominateColor: player.player_image_dominant_color,
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

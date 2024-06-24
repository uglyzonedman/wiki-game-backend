import { PrismaClient } from '@prisma/client'
import bodyParser from 'body-parser'
import cors from 'cors'
import express from 'express'
import log4js from 'log4js'
import team_router from '../src/routes/team.router'
const app = express()
const port = process.env.PORT || 8080
const prisma = new PrismaClient()

log4js.configure({
	appenders: {
		console: { type: 'console' },
		file: { type: 'file', filename: 'logs/app.log' },
	},
	categories: {
		default: { appenders: ['console', 'file'], level: 'debug' },
	},
})

const logger = log4js.getLogger()

app.use(bodyParser.json())

const corsOptions = {
	origin: 'http://localhost:3000',
	methods: ['GET', 'POST', 'PUT', 'DELETE'],
	allowedHeaders: ['Content-Type', 'Authorization'],
	credentials: true,
}

app.use(cors(corsOptions))

app.use((req, res, next) => {
	logger.debug(`Request received: ${req.method} ${req.url}`)
	next()
})

app.use('/teams', team_router)

app.get('/', (request, response) => {
	logger.info('Handling / endpoint')
	response.send('ZOV GOIDA!')
})

app.listen(port, () => {
	logger.info(`Server is running on port http://localhost:${port}`)
})

require('dotenv').config();
const express = require('express');
const { createClient } = require('redis');
const bodyParser = require('body-parser');
const path = require('path');

const app = express();
const port = 3000;

// Middleware
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, '.'))); // Serve static files from current directory

// Redis Client
const client = createClient({
    username: process.env.REDIS_USERNAME || 'default',
    password: process.env.REDIS_PASSWORD,
    socket: {
        host: process.env.REDIS_HOST,
        port: process.env.REDIS_PORT
    }
});

client.on('error', (err) => console.log('Redis Client Error', err));

async function connectRedis() {
    await client.connect();
}
connectRedis();

// Routes
app.get('/record', async (req, res) => {
    try {
        const value = await client.get('tictactoe_game');
        // If no game saved, return empty board or default
        // The frontend expects a string of length 9, e.g., "@@@@@@@@@"
        res.send(value || '@@@@@@@@@');
    } catch (err) {
        console.error(err);
        res.status(500).send('Error retrieving game state');
    }
});

app.post('/save', async (req, res) => {
    try {
        const { state } = req.body;
        await client.set('tictactoe_game', state);
        res.send('Game saved');
    } catch (err) {
        console.error(err);
        res.status(500).send('Error saving game state');
    }
});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});

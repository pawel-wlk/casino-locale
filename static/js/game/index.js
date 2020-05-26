import {
    CardEngine
} from '../modules/CardEngine.js';
import {
    Card,
    defaultColors
} from '../modules/Card.js';
import {
    Animation,
    createDefaultCallback
} from '../modules/Animation.js';
import {
    Token,
    defaultValues
} from '../modules/Token.js';
import {
    Blackjack
} from '../modules/blackjack/Blackjack.js';

window.addEventListener('load', () => {
    const roomName = JSON.parse(document.getElementById('room-name').textContent);
    const gameSocket = new WebSocket(`ws://${window.location.host}/ws/room/${roomName}/`);

    const inputs = document.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('click', event => {
            const payload = {
                type: event.target.dataset['action'] === 'ready' ? 'init' : 'move',
                message: {
                    action: event.target.dataset['action']
                }
            };

            if (event.target.dataset['action'] === 'bet') {
                payload.message.value = Number.parseInt(document.getElementById('bet-value').value);
            }

            gameSocket.send(JSON.stringify(payload));
        });
    });

    gameSocket.addEventListener('message', message => {
        const availableMoves = JSON.parse(message.data)
            .message
            .players[0]
            // .find(p => p.player === 'TODO')
            .available_moves;

        inputs.forEach(input => {
            input.disabled = !availableMoves.includes(input.dataset['action']);
        })
    });

    const engine = new CardEngine(document.querySelector('canvas'));
    const blackjack = new Blackjack(gameSocket, engine);

    function draw(time) {
        requestAnimationFrame(draw);
        engine.draw(time);
    }
    draw(0);
});
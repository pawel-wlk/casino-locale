import {
    CardEngine
} from '../modules/CardEngine.js';
import {
    Poker
} from '../modules/poker/Poker.js';

window.addEventListener('load', () => {
    const roomName = JSON.parse(document.getElementById('room-name').textContent);

    const potSum = document.getElementById('pot-sum');
    const yourBalance = document.getElementById('your-balance');
    const gameSocket = new WebSocket(`ws://${window.location.host}/ws/room/${roomName}/`);

    const playerList = document.getElementById('player-list');

    const inputs = document.querySelectorAll('input');
    inputs.forEach(input => {
        if (input.type !== 'number')
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

                if (event.target.dataset['action'] === 'raise') {
                    payload.message.value = Number.parseInt(document.getElementById('raise-value').value);
                }

                gameSocket.send(JSON.stringify(payload));
            });
    });

    gameSocket.addEventListener('message', message => {
        const data = JSON.parse(message.data); // parse data

        if (data.message.player) {
            inputs.forEach(input => {
                input.disabled = !data.message.player.available_moves.includes(input.dataset['action']);
            });
        }

        if (data.message.players) {
            data.message.players.forEach(player => {
                const row = document.createElement('tr');
                const name = document.createElement('td');
                const status = document.createElement('td');

                name.textContent = player.player;
                status.textContent = player.status;

                row.append(name, status);
                playerList.append(row);
            });
        }

        potSum.textContent = data.message.pot;
        yourBalance.textContent = data.message.player.balance;
    });

    const engine = new CardEngine(document.querySelector('canvas'));
    const poker = new Poker(gameSocket, engine);

    function draw(time) {
        requestAnimationFrame(draw);
        engine.draw(time);
    }
    draw(0);
});
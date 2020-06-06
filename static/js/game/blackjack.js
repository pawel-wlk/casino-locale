import {
    CardEngine
} from '../modules/CardEngine.js';
import {
    Blackjack
} from '../modules/blackjack/Blackjack.js';

window.addEventListener('load', () => {
    const roomName = JSON.parse(document.getElementById('room-name').textContent);
    const userId = JSON.parse(document.getElementById('user-id').textContent);

    const playerList = document.getElementById('player-list');
    const croupierSum = document.getElementById('croupier-sum');
    const gameSocket = new WebSocket(`ws://${window.location.host}/ws/room/${roomName}/`);

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

                gameSocket.send(JSON.stringify(payload));
            });
    });

    gameSocket.addEventListener('message', message => {
        const data = JSON.parse(message.data); // parse data

        const availableMoves = data.message.players.find(p => p.player === userId).available_moves; // update actions
        inputs.forEach(input => {
            input.disabled = !availableMoves.includes(input.dataset['action']);
        });

        croupierSum.textContent = data.message.croupier.sum; // update croupier text

        while (playerList.firstChild) playerList.removeChild(playerList.firstChild); // update players table
        data.message.players.forEach(player => {
            const row = document.createElement('tr');
            const name = document.createElement('td');
            const sum = document.createElement('td');
            const balance = document.createElement('td');

            name.textContent = player.player;
            sum.textContent = player.sum;
            balance.textContent = player.balance;

            row.append(name, sum, balance);
            playerList.append(row);
        });
    });

    const engine = new CardEngine(document.querySelector('canvas'));
    const blackjack = new Blackjack(gameSocket, engine);

    function draw(time) {
        requestAnimationFrame(draw);
        engine.draw(time);
    }
    draw(0);
});
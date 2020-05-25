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

    const chatSocket = new WebSocket(
        'ws://' +
        window.location.host +
        '/ws/room/' +
        roomName +
        '/'
    );

    chatSocket.onclose = function (e) {
        console.error('Chat socket closed unexpectedly');
    };

    document.querySelector('#chat-message-input').focus();
    document.querySelector('#chat-message-input').onkeyup = function (e) {
        if (e.keyCode === 13) { // enter, return
            document.querySelector('#chat-message-submit').click();
        }
    };

    document.querySelector('#chat-message-submit').onclick = function (e) {
        const messageInputDom = document.querySelector('#chat-message-input');
        const message = messageInputDom.value;
        chatSocket.send(JSON.stringify({
            'message': message,
            'type': 'not_move'
        }));
        messageInputDom.value = '';
    };

    document.querySelector('#hit').onclick = function (e) {
        chatSocket.send(JSON.stringify({
            'type': 'move',
            'message': {
                'action': 'hit'
            }
        }))
    }

    document.querySelector('#stand').onclick = function (e) {
        chatSocket.send(JSON.stringify({
            'type': 'move',
            'message': {
                'action': 'stand'
            }
        }))
    }

    document.querySelector('#ready').onclick = function (e) {
        chatSocket.send(JSON.stringify({
            'type': 'init',
            'message': {
                'action': 'ready'
            }
        }))
    }

    document.querySelector('#split').onclick = function (e) {
        chatSocket.send(JSON.stringify({
            'type': 'move',
            'message': {
                'action': 'split'
            }
        }))
    }

    document.querySelector('#double').onclick = function (e) {
        chatSocket.send(JSON.stringify({
            'type': 'move',
            'message': {
                'action': 'double'
            }
        }))
    }


    document.querySelector('#bet').onclick = function (e) {
        const messageInputDom = document.querySelector('#chat-message-input');
        const message = messageInputDom.value;
        chatSocket.send(JSON.stringify({
            'type': 'move',
            'message': {
                'action': 'bet',
                'value': parseInt(message)
            }
        }))
    }

    const engine = new CardEngine(document.querySelector('canvas'));
    const blackjack = new Blackjack(chatSocket, engine);

    function draw(time) {
        requestAnimationFrame(draw);
        engine.draw(time);
    }
    draw(0);
});
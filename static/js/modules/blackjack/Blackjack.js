import {
    AnimationScheduler
} from '../AnimationScheduler.js';

import {
    BlackjackPlayer
} from './Player.js';

import {
    Animation,
    createDefaultCallback
} from '../Animation.js';

import {
    CardDeck
} from '../CardDeck.js';

export const defaultConfig = {
    animationDuration: 500,
    deckPosition: {
        x: 0,
        y: 0
    }
};

export class Blackjack {
    constructor(websocket, cardEngine, blackjackConfig = defaultConfig) {
        this.cardEngine = cardEngine;
        this.config = blackjackConfig;

        this.deck = new CardDeck(true);
        this.animationScheduler = new AnimationScheduler(this.cardEngine);
        this.players = [];
        this.croupier = new BlackjackPlayer('', {
            x: 300,
            y: 100
        });

        websocket.addEventListener('message', m => {
            this.parseMessage(m.data);
        });
    }

    parseMessage(message) {
        const data = JSON.parse(message);
        console.log('Message:', data);

        data.message.croupier.hand.forEach(cardInfo => {
            this.updatePlayerCard(cardInfo, this.croupier, 0);
        });

        data.message.players.forEach(player => {
            const playerObject = this.updatePlayer(player.player);
            player.hand.forEach(cardInfo => {
                this.updatePlayerCard(cardInfo, playerObject, 0); //TODO: resolve hand issues
            });
        });
    }

    updatePlayer(id) {
        let player = this.players.find(player => player.id === id);
        if (!player) {
            player = new BlackjackPlayer(id, {
                x: 300,
                y: 300
            })
            this.players.push(player); // TODO: proper locations
        }

        console.log('Updating player...', player);

        return player;
    }

    offsetCardLocation(baseLocation, cardNumber) {
        return {
            x: baseLocation.x + this.cardEngine.config.base * this.cardEngine.config.cardWidth / 2 * (cardNumber - 1),
            y: baseLocation.y + this.cardEngine.config.base * this.cardEngine.config.cardWidth / 2 * (cardNumber - 1),
        };
    }

    updatePlayerCard(cardInfo, player, hand) {
        const card = this.deck.getCard(cardInfo);
        if (player.hands.some(hand => hand.includes(card))) return;

        if (player.hands[hand]) player.hands[hand].push(card);
        else player.hands[hand] = [card];

        console.log('Updating card...', card, player, hand);

        this.cardEngine.objects.push(card);
        this.animationScheduler.animateWith(
            new Animation(
                0,
                this.config.animationDuration,
                createDefaultCallback.position(
                    card,
                    this.config.deckPosition,
                    this.offsetCardLocation(player.location, player.hands[hand].length)
                )
            )
        );
    }
}
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
        x: 1 / 2,
        y: -2
    }
};

export class Blackjack {
    constructor(websocket, cardEngine, blackjackConfig = defaultConfig) {
        this.cardEngine = cardEngine;
        this.config = {
            ...blackjackConfig,
            deckPosition: {
                x: (blackjackConfig.deckPosition.x - cardEngine.config.cardWidth / 2) * cardEngine.config.base,
                y: blackjackConfig.deckPosition.y * cardEngine.config.cardHeight * cardEngine.config.base
            },
            maxHandWidth: this.cardEngine.config.base * this.cardEngine.config.cardWidth * 3
        };

        this.animationScheduler = new AnimationScheduler(this.cardEngine);
        this.decks = [
            new CardDeck(true, this.config.deckPosition),
            new CardDeck(true, this.config.deckPosition)
        ];
        this.players = [];
        this.croupier = new BlackjackPlayer('', {
            x: this.cardEngine.config.width / 2,
            y: this.cardEngine.config.cardHeight * this.cardEngine.config.base / 2
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
            player.hand.forEach((hand, handIndex) => { // new version
                hand.forEach(cardInfo => {
                    this.updatePlayerCard(cardInfo, playerObject, handIndex);
                });
            });
        });
    }

    updatePlayer(id) {
        let player = this.players.find(player => player.id === id);
        if (!player) {
            player = new BlackjackPlayer(id, {
                x: this.config.maxHandWidth * (this.players.length + 1),
                y: 300
            });
            this.players.push(player); // TODO: proper locations
        }

        console.log('Updating player...', player);

        return player;
    }

    offsetCardLocation(player, handIndex) {
        const baseX = player.location.x + (handIndex - player.hands.length / 2) * this.config.maxHandWidth;

        return {
            x: baseX + this.cardEngine.config.base * this.cardEngine.config.cardWidth / 2 * (player.hands[handIndex].length - 1),
            y: player.location.y + this.cardEngine.config.base * this.cardEngine.config.cardWidth / 2 * (player.hands[handIndex].length - 1),
        };
    }

    updatePlayerCard(cardInfo, player, handIndex) {
        const cards = this.decks.map(deck => deck.getCard(cardInfo));
        const card = cards[0];

        const handHoldingCard = player.hands.find(hand => hand.includes(card));
        if (player.hands.length === 0) { // special case for none cards
            player.hands.push([card]);
        } else if (handIndex > player.hands.length - 1) { // card in a new hand - was splitted
            handHoldingCard.splice(handHoldingCard.indexOf(card), 1); // remove card from the hand
            player.hands.push([card]); // add a new hand with the card
        } else { // card in existing hand - do nothing
            if (handHoldingCard) return;
            if (player.hands[handIndex].push(card));
        }

        console.log('Updating card...', card, player, handIndex);

        this.cardEngine.objects.push(card);
        this.animationScheduler.animateAfter(
            new Animation(
                0,
                this.config.animationDuration,
                createDefaultCallback.position(
                    card,
                    card.position,
                    this.offsetCardLocation(player, handIndex)
                )
            )
        );
    }
}
import {
    AnimationScheduler,
} from '../AnimationScheduler.js';

import {
    Animation,
    createDefaultCallback
} from '../Animation.js';

import {
    PokerPlayer,
    PokerPlayerHand
} from './Player.js';

import {
    CardDeck
} from '../CardDeck.js';

export const defaultConfig = {
    animationDuration: 500,
    deckPosition: {
        x: 1 / 2,
        y: -2
    }
}

export class Poker {
    constructor(websocket, cardEngine, pokerConifg = defaultConfig) {
        this.cardEngine = cardEngine;
        this.config = {
            ...pokerConifg,
            deckPosition: {
                x: (pokerConifg.deckPosition.x - cardEngine.config.cardWidth / 2) * cardEngine.config.base,
                y: pokerConifg.deckPosition.y * cardEngine.config.cardHeight * cardEngine.config.base
            }
        };

        this.animationScheduler = new AnimationScheduler(this.cardEngine);
        this.decks = [
            new CardDeck(true, this.config.deckPosition),
            new CardDeck(true, this.config.deckPosition)
        ];

        this.table = new PokerPlayer('', {
            x: this.cardEngine.config.width / 2 - 2 * this.cardEngine.config.base * this.cardEngine.config.cardWidth,
            y: this.cardEngine.config.cardHeight * this.cardEngine.config.base / 2
        });
        this.player = new PokerPlayer('player', {
            x: this.cardEngine.config.width / 2 - 1.25 * this.cardEngine.config.base * this.cardEngine.config.cardWidth,
            y: this.cardEngine.config.height - this.cardEngine.config.cardHeight * this.cardEngine.config.base * 2
        });

        console.log('Initiated:', this.player, this.table);

        websocket.addEventListener('message', m => {
            this.parseMessage(m.data);
        });
    }

    parseMessage(message) {
        const data = JSON.parse(message);
        console.log('Message:', data);

        const tableHand = new PokerPlayerHand(data.message.table_cards);
        this.table.hand.diffWithHand(tableHand).forEach(card => {
            this.addCardFromDeck(this.table, card);
        });

        const playerHand = new PokerPlayerHand(data.message.player.hand);
        this.player.hand.diffWithHand(playerHand).forEach(card => {
            this.addCardFromDeck(this.player, card);
        });
    }

    offsetCardLocation(player, cardNo) {
        return {
            x: player.location.x + 1.5 * cardNo * this.cardEngine.config.cardWidth * this.cardEngine.config.base,
            y: player.location.y
        };
    }

    addCardFromDeck(player, cardToAdd) {
        let card = null;
        for (let deck of this.decks) {
            if (card = deck.getCard(cardToAdd)) break;
        }

        if (card === null) {
            console.error('There are no more cards like that in decks');
            return;
        }

        console.log('Adding new card from deck...', card);

        console.log(player)
        player.hand.cards.push(card);
        this.cardEngine.objects.push(card);
        this.animationScheduler.animateAfter(
            new Animation(
                0,
                this.config.animationDuration,
                createDefaultCallback.position(
                    card,
                    card.position,
                    this.offsetCardLocation(player, player.hand.cards.length - 1)
                )
            )
        );
    }
}
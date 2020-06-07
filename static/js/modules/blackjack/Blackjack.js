import {
    AnimationScheduler
} from '../AnimationScheduler.js';
import {
    BlackjackPlayer,
    BlackjackPlayerHand
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
        this.croupier.hands.push(new BlackjackPlayerHand()); // croupier has one hand

        websocket.addEventListener('message', m => {
            this.parseMessage(m.data);
        });
    }

    parseMessage(message) {
        const data = JSON.parse(message);
        console.log('Message:', data);

        const croupierHand = new BlackjackPlayerHand(data.message.croupier.hand);
        this.croupier.hands[0].diffWithHand(croupierHand).forEach(card => {
            this.addPlayerCardFromDeck(this.croupier, 0, card);
        });

        data.message.players.forEach(player => {
            const playerObject = this.updatePlayer(player.player);
            player.hand.forEach((hand, handIndex) => {
                if (hand.length === 0) return; // we don't want to include the empty hands

                const handObject = new BlackjackPlayerHand(hand);
                let playerHand = playerObject.hands[handIndex];

                if (!playerHand) { // split or just new game
                    playerHand = (playerObject.hands[handIndex] = new BlackjackPlayerHand()); // create the hand
                    let done = false; // flag to stop iteration
                    for (let h of playerObject.hands) { // check previous hands...
                        const diff = handObject.diffWithHand(h); // diff the message hand
                        if (diff.length) { // current hand holds more cards than message hand - was splitted
                            for (let i = h.cards.length - 1; i >= 0 && !done; i--) { // find duplicate card
                                for (let j = i; j >= 0 && !done; j--) {
                                    if (h.cards[i].compareWith(h.cards[j])) {
                                        const cardToSplit = h.cards.splice(i, 1)[0];
                                        this.addPlayerCardFromSplit(playerObject, handIndex, cardToSplit);
                                        done = true;
                                    }
                                }
                            }
                        }
                        if (done) break;
                    }
                }

                const diff = playerHand.diffWithHand(handObject);
                diff.forEach(card => this.addPlayerCardFromDeck(playerObject, handIndex, card));
            });
        });
    }

    updatePlayer(id) {
        let player = this.players.find(player => player.id === id);
        if (!player) {
            player = new BlackjackPlayer(id, {
                x: this.config.maxHandWidth * (this.players.length + 0.5),
                y: 500
            });
            this.players.push(player);

            console.log('Adding new player...', player);
        }

        return player;
    }

    offsetCardLocation(player, handIndex) {
        return {
            x: handIndex * this.config.maxHandWidth / 2 + player.location.x + this.cardEngine.config.base * this.cardEngine.config.cardWidth / 2 * (player.hands[handIndex].cards.length - 1),
            y: player.location.y + this.cardEngine.config.base * this.cardEngine.config.cardWidth / 2 * (player.hands[handIndex].cards.length - 1),
        };
    }

    addPlayerCardFromDeck(player, handIndex, cardToAdd) {
        let card = null;
        for (let deck of this.decks) {
            if (card = deck.getCard(cardToAdd)) break;
        }

        if (card === null) {
            console.error('There are no more cards like that in decks');
            return;
        }

        console.log('Adding new card from deck...', card);

        player.hands[handIndex].cards.push(card);
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

    addPlayerCardFromSplit(player, handIndex, cardToMove) {
        player.hands[handIndex].cards.push(cardToMove);
        this.animationScheduler.animateAfter(
            new Animation(
                0,
                this.config.animationDuration,
                createDefaultCallback.position(
                    cardToMove,
                    cardToMove.position,
                    this.offsetCardLocation(player, handIndex)
                )
            )
        );
    }
}
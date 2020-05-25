import {
    Card,
    defaultColors,
    defaultRanks,
    defaultCardConfig
} from './Card.js';

export class CardDeck {
    constructor(initializeWithDefault = false, cardConfig = defaultCardConfig) {
        this.cards = [];
        if (initializeWithDefault) {
            for (let rank of Object.values(defaultRanks)) {
                for (let color of Object.values(defaultColors)) {
                    this.cards.push(new Card(rank, color, cardConfig));
                }
            }
        }
    }

    getCard(cardInfo) {
        return this.cards.find(card => card.rank === defaultRanks[cardInfo.rank] && card.color === defaultColors[cardInfo.suit]);
    }
}
import {
    Card,
    defaultColors,
    defaultRanks,
    defaultCardConfig
} from './Card.js';

export class CardDeck {
    constructor(
        initializeWithDefault = false,
        defaultPosition = {
            x: 0,
            y: 0
        },
        cardConfig = defaultCardConfig
    ) {
        this.cards = [];
        if (initializeWithDefault) {
            for (let rank of Object.values(defaultRanks)) {
                for (let color of Object.values(defaultColors)) {
                    const card = new Card(rank, color, cardConfig);
                    card.position = {
                        ...defaultPosition
                    };
                    this.cards.push(card);
                }
            }
        }
    }

    getCard(cardInfo) {
        return this.cards.find(card => card.rank === defaultRanks[cardInfo.rank] && card.color === defaultColors[cardInfo.suit]);
    }
}
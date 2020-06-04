import { defaultCardConfig, Card } from "../Card.js";

export class BlackjackPlayerHand {
    constructor(handInfo = [], cardConfig = defaultCardConfig) {
        this.cards = handInfo.map(cardInfo => Card.fromCardInfo(cardInfo, cardConfig));
    }

    diffWithHand(otherHand) {
        const cardsCopy = [...this.cards];
        const result = [];
        for (let card of otherHand.cards) {
            const index = cardsCopy.findIndex(c => c.compareWith(card));
            if (index > -1) {
                cardsCopy.splice(index, 1);
            } else {
                result.push(card);
            }
        }
        return result;
    }
}

export class BlackjackPlayer {
    constructor(id, location) {
        this.id = id;
        this.location = location;
        this.hands = [];
    }
}
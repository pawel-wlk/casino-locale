export class CardColor {
    constructor(displayName, symbol, color) {
        this.displayName = displayName;
        this.symbol = symbol;
        this.color = color;
    }
}

export const defaultColors = {
    clubs: new CardColor('Clubs', '♣', '#000000'),
    spades: new CardColor('Spades', '♠', "#000000"),
    hearts: new CardColor('Hearts', '♥', '#ff0000'),
    diamons: new CardColor('Diamons', '♦', '#ff000000')
};

export const defaultCardConfig = {
    selectable = false,
    selected = false,
};

export class Card {
    constructor(rank, color, cardConfig = defaultCardConfig) {
        this.rank = rank;
        this.color = color;
        this.config = cardConfig;

        this.position = { // top-left corner
            x: 0,
            y: 0,
            z: 0
        };
    }

    inBoundary(pointerPosition, engineConfig) {
        return pointerPosition.x >= this.position.x &&
            pointerPosition.x <= this.position.x + engineConfig.cardWidth * engineConfig.width &&
            pointerPosition.y >= this.position.y &&
            pointerPosition.y <= this.position.y + engineConfig.cardHeight * engineConfig.height;
    }
}

export const defaultEngineConfig = {
    cardHeight: 1 / 10,
    cardWidth: 1 / 14,
    
};

export class CardEngine {
    constructor(canvasElement, engineConfig = defaultEngineConfig) {
        this.cardSize = cardSize;
        this.config = {
            height: canvasElement.height,
            width: canvasElement.width,
            ...engineConfig
        };
        this.ctx = canvasElement.getContext('2d');
        this.cards = [];

        canvasElement.addEventListeners('pointermove', event => {

        });
    }

    handleSelection(pointerPosition) {
        const highestZCard = null;

        this.cards.forEach(card => {
            if (card.inBoundary(pointerPosition, this.config)) {
                if (card.config.selectable) {
                    if (highestZCard === null || highestZCard.position.z < card.position.z) highestZCard = card;
                }
            } else {
                if (card.config.selectable) card.config.selected = false;
            }
        });

        if (highestZCard) highestZCard.config.selected = true;
    }
}
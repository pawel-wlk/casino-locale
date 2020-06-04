export const defaultRanks = {
    ONE: '1',
    TWO: '2',
    THREE: '3',
    FOUR: '4',
    FIVE: '5',
    SIX: '6',
    SEVEN: '7',
    EIGHT: '8',
    NINE: '9',
    TEN: '10',
    JACK: 'J',
    QUEEN: 'Q',
    KING: 'K',
    ACE: 'A'
};

export class CardColor {
    constructor(displayName, symbol, color) {
        this.displayName = displayName;
        this.symbol = symbol;
        this.color = color;
    }
}

export const defaultColors = {
    CLUBS: new CardColor('Clubs', '♣', '#2A2D34'),
    SPADES: new CardColor('Spades', '♠', "#2A2D34"),
    HEARTS: new CardColor('Hearts', '♥', '#B10F2E'),
    DIAMONDS: new CardColor('Diamons', '♦', '#B10F2E')
};

export const defaultCardConfig = {
    selectable: false,
    selected: false,
    bakcground: '#4062BB',
    selectedBackground: '#304a8c',
};

export class Card /* implements GameObject */ {
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

    static fromCardInfo(cardInfo, cardConfig = defaultCardConfig, ranks = defaultRanks, colors = defaultColors) {
        return new Card(ranks[cardInfo.rank], colors[cardInfo.suit], cardConfig);
    }

    inBoundary(pointerEvent, engineConfig) {
        return pointerEvent.layerX >= this.position.x &&
            pointerEvent.layerX <= this.position.x + engineConfig.cardWidth * engineConfig.base &&
            pointerEvent.layerY >= this.position.y &&
            pointerEvent.layerY <= this.position.y + engineConfig.cardHeight * engineConfig.base;
    }

    drawMe(context, engineConfig) {
        context.fillStyle = this.config.selected ? this.config.selectedBackground : this.config.bakcground;
        context.shadowColor = 'rgba(0, 0, 0, 0.5)';
        context.shadowBlur = 10;
        context.fillRect(
            this.position.x,
            this.position.y,
            engineConfig.cardWidth * engineConfig.base,
            engineConfig.cardHeight * engineConfig.base
        );

        context.shadowColor = 'transparent';
        context.textBaseline = 'top';
        context.fillStyle = this.color.color;
        context.font = `${engineConfig.cardHeight * engineConfig.base / 4}px monospace`;
        context.fillText(`${this.rank}${this.color.symbol}`,
            this.position.x + engineConfig.cardHeight * engineConfig.base / 32,
            this.position.y + engineConfig.cardWidth * engineConfig.base / 32);
    }

    compareWith(card) {
        return this.rank === card.rank && this.color === card.color;
    }
}
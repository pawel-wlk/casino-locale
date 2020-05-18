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
    selectable: true,
    selected: false,
    bakcground: '#0070ff',
    selectedBackground: '#0050df',
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

    inBoundary(pointerEvent, engineConfig) {
        return pointerEvent.layerX >= this.position.x &&
            pointerEvent.layerX <= this.position.x + engineConfig.cardWidth * engineConfig.width &&
            pointerEvent.layerY >= this.position.y &&
            pointerEvent.layerY <= this.position.y + engineConfig.cardHeight * engineConfig.height;
    }

    drawMe(context, engineConfig) {
        context.fillStyle = this.config.selected ? this.config.selectedBackground : this.config.bakcground;
        context.fillRect(
            this.position.x,
            this.position.y,
            engineConfig.cardWidth * engineConfig.width,
            engineConfig.cardHeight * engineConfig.height
        );
    }
}
export class CardColor {
    constructor(displayName, symbol, color) {
        this.displayName = displayName;
        this.symbol = symbol;
        this.color = color;
    }
}

export const defaultColors = {
    clubs: new CardColor('Clubs', '♣', '#2A2D34'),
    spades: new CardColor('Spades', '♠', "#2A2D34"),
    hearts: new CardColor('Hearts', '♥', '#B10F2E'),
    diamons: new CardColor('Diamons', '♦', '#B10F2E')
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

    inBoundary(pointerEvent, engineConfig) {
        return pointerEvent.layerX >= this.position.x &&
            pointerEvent.layerX <= this.position.x + engineConfig.cardWidth * engineConfig.base &&
            pointerEvent.layerY >= this.position.y &&
            pointerEvent.layerY <= this.position.y + engineConfig.cardHeight * engineConfig.base;
    }

    drawMe(context, engineConfig) {
        context.fillStyle = this.config.selected ? this.config.selectedBackground : this.config.bakcground;
        context.fillRect(
            this.position.x,
            this.position.y,
            engineConfig.cardWidth * engineConfig.base,
            engineConfig.cardHeight * engineConfig.base
        );
        context.textBaseline = 'top';
        context.fillStyle = this.color.color;
        context.font = `${engineConfig.cardHeight * engineConfig.base / 4}px monospace`;
        context.fillText(`${this.rank}${this.color.symbol}`,
            this.position.x + engineConfig.cardHeight * engineConfig.base / 32,
            this.position.y + engineConfig.cardWidth * engineConfig.base / 32);
    }
}
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
    bakcground: '#0070ff'
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
        context.fillStyle = this.config.bakcground;
        context.fillRect(
            this.position.x,
            this.position.y,
            engineConfig.cardWidth * engineConfig.width,
            engineConfig.cardHeight * engineConfig.height
        );
    }
}

export const defaultEngineConfig = {
    cardHeight: 1 / 10,
    cardWidth: 1 / 14,
    background: 'transparent'
};

export class CardEngine {
    constructor(canvasElement, engineConfig = defaultEngineConfig) {
        this.config = {
            height: canvasElement.height,
            width: canvasElement.width,
            ...engineConfig
        };
        this.ctx = canvasElement.getContext('2d');
        this.cards = [];
        this.dragged = {
            card: null,
            lastX: 0,
            lastY: 0,
        };

        canvasElement.addEventListener('pointermove', event => {
            if (this.dragged.card) {
                this.dragged.card.position.x -= this.dragged.lastX - (this.dragged.lastX = event.layerX);
                this.dragged.card.position.y -= this.dragged.lastY - (this.dragged.lastY = event.layerY);
            } else {
                this.handleSelection(event);
            }
        });

        canvasElement.addEventListener('mousedown', event => {
            if (this.dragged.card = this.handleSelection(event)) {
                this.dragged.lastX = event.layerX;
                this.dragged.lastY = event.layerY;
                this.dragged.card.position.z++;
            }
        });

        canvasElement.addEventListener('pointerout', () => this.dragged.card = null);
        canvasElement.addEventListener('mouseup', () => this.dragged.card = null);
    }

    handleSelection(pointerEvent) {
        let highestZCard = null;

        this.cards.forEach(card => {
            if (card.inBoundary(pointerEvent, this.config)) {
                if (card.config.selectable) {
                    if (highestZCard === null || highestZCard.position.z < card.position.z) {
                        highestZCard = card;
                    }
                }
            } else {
                if (card.config.selectable) card.config.selected = false;
            }
        });

        if (highestZCard) {
            highestZCard.config.selected = true;
        }
        return highestZCard;
    }

    draw() {
        this.ctx.clearRect(0, 0, this.config.width, this.config.height);
        this.cards.forEach(card => card.drawMe(this.ctx, this.config));
    }
}
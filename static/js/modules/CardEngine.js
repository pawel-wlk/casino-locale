export const defaultEngineConfig = {
    cardHeight: 1 / 10,
    cardWidth: 1 / 14,
    background: 'transparent'
};

export class CardEngine {
    constructor(canvasElement, engineConfig = defaultEngineConfig) {
        this.config = {
            ...engineConfig,
            height: canvasElement.height,
            width: canvasElement.width,
            cardHeight: engineConfig.cardHeight / (canvasElement.height / canvasElement.width)
        };
        this.ctx = canvasElement.getContext('2d');
        this.cards = [];
        this.animations = [];
        this.dragged = {
            object: null,
            lastX: 0,
            lastY: 0,
        };

        canvasElement.addEventListener('pointermove', event => {
            if (this.dragged.object) {
                this.dragged.object.position.x -= this.dragged.lastX - event.layerX;
                this.dragged.object.position.y -= this.dragged.lastY - event.layerY;
            } else {
                this.handleSelection(event);
            }
            this.dragged.lastX = event.layerX;
            this.dragged.lastY = event.layerY;
        });

        canvasElement.addEventListener('mousedown', event => {
            if (this.dragged.object = this.handleSelection(event)) {
                this.dragged.lastX = event.layerX;
                this.dragged.lastY = event.layerY;
                this.dragged.object.position.z++;
            }
        });

        canvasElement.addEventListener('pointerout', () => this.dragged.object = null);
        canvasElement.addEventListener('mouseup', () => this.dragged.object = null);
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

    draw(time) {
        this.ctx.clearRect(0, 0, this.config.width, this.config.height);
        this.animations = this.animations.filter(animation => {
            if (animation.startTime <= time && time - animation.startTime <= animation.duration) {
                animation.setAt(time);
                this.handleSelection({
                    layerX: this.dragged.lastX,
                    layerY: this.dragged.lastY
                });
            }
            return animation.startTime + animation.duration > time;
        });
        this.cards.forEach(card => card.drawMe(this.ctx, this.config));
    }
}
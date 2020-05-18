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
        this.animations = [];
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

        // we probably dont need this at all :((((
        // canvasElement.addEventListener('mousedown', event => {
        //     if (this.dragged.card = this.handleSelection(event)) {
        //         this.dragged.lastX = event.layerX;
        //         this.dragged.lastY = event.layerY;
        //         this.dragged.card.position.z++;
        //     }
        // });

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

    draw(time) {
        this.ctx.clearRect(0, 0, this.config.width, this.config.height);
        this.animations = this.animations.filter(animation => {
            if (animation.startTime <= time && time - animation.startTime <= animation.duration) {
                animation.setAt(time);
            }
            return animation.startTime + animation.duration > time;
        });
        this.cards.forEach(card => card.drawMe(this.ctx, this.config));
    }
}
export const defaultEngineConfig = {
    cardHeight: 1 / 10,
    cardWidth: 1 / 14,
    tokenRadius: 1 / 28,
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
        this.objects = [];
        this.animations = [];
        this.dragged = {
            object: null,
            lastX: 0,
            lastY: 0,
        };

        canvasElement.addEventListener('pointermove', event => {
            if (this.dragged.object) {
                canvasElement.style.cursor = 'grabbing';
                this.dragged.object.position.x -= this.dragged.lastX - event.layerX;
                this.dragged.object.position.y -= this.dragged.lastY - event.layerY;
            } else {
                if (this.handleSelection(event)) {
                    canvasElement.style.cursor = 'grab';
                } else {
                    canvasElement.style.cursor = 'auto';
                }
            }
            this.dragged.lastX = event.layerX;
            this.dragged.lastY = event.layerY;
        });

        canvasElement.addEventListener('mousedown', event => {
            if (this.dragged.object = this.handleSelection(event)) {
                canvasElement.style.cursor = 'grabbing';
            }
        });

        canvasElement.addEventListener('pointerout', () => this.dragged.object = null);
        canvasElement.addEventListener('mouseup', () => {
            this.dragged.object = null;
            canvasElement.style.cursor = 'grab';
        });
    }

    handleSelection(pointerEvent) {
        let highestZObject = null;

        this.objects.forEach(object => {
            if (object.inBoundary(pointerEvent, this.config)) {
                if (object.config.selectable) {
                    if (highestZObject === null || highestZObject.position.z < object.position.z) {
                        highestZObject = object;
                    }
                }
            } else {
                if (object.config.selectable) object.config.selected = false;
            }
        });

        if (highestZObject) {
            highestZObject.config.selected = true;
        }
        return highestZObject;
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
        this.objects.forEach(object => object.drawMe(this.ctx, this.config));
    }
}
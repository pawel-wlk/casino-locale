export class TokenValue {
    constructor(number, color, rim) {
        this.number = number;
        this.color = color;
        this.rim = rim;
    }
}

export const defaultValues = {
    1000: new TokenValue(1000, '#2A2D34', '#1A1D24')
};

export const defaultTokenConfig = {
    selectable: true,
    selected: false
};

export class Token {
    constructor(value, tokenConfig = defaultTokenConfig) {
        this.value = value;
        this.config = defaultTokenConfig;

        this.position = { // center
            x: 0,
            y: 0,
            z: 0
        };
    }

    inBoundary(pointerEvent, engineConfig) {
        return Math.sqrt((pointerEvent.layerX - this.position.x) ** 2 + (pointerEvent.layerY - this.position.y) ** 2) < engineConfig.tokenRadius * engineConfig.width;
    }

    drawMe(context, engineConfig) {
        context.fillStyle = this.value.rim;
        context.beginPath();
        context.arc(
            this.position.x,
            this.position.y,
            engineConfig.tokenRadius * engineConfig.width,
            0,
            2 * Math.PI
        );
        context.fill();
        context.beginPath();
        context.fillStyle = this.value.color;
        context.arc(
            this.position.x,
            this.position.y,
            0.8 * engineConfig.tokenRadius * engineConfig.width,
            0,
            2 * Math.PI
        );
        context.fill();
    }
}
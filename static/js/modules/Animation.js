export const createDefaultCallback = {
    position: (pos, start, end) => progress => {
        pos.x = (1 - progress) * start.x + progress * end.x;
        pos.y = (1 - progress) * start.y + progress * end.y;
    }
}

export class Animation {
    constructor(startTime, duration, changeCallback) {
        this.startTime = startTime;
        this.duration = duration;
        this.changeCallback = changeCallback;
    }

    setAt(time) { // linear only for now
        this.changeCallback(Math.min(1, (time - this.startTime) / this.duration));
    }
}
export const createDefaultCallback = {
    position: (object, start, end) => progress => {
        object.position.x = (1 - progress) * start.x + progress * end.x;
        object.position.y = (1 - progress) * start.y + progress * end.y;
    }
}

export const defaultEasings = {
    linear: x => x,
    cubicInOut: x => x < 0.5 ? 2 * x ** 2 : -2 * x ** 2 + 4 * x - 1,
    cubinIn: x => x ** 2,
    cubicOut: x => 2 * x - x ** 2
}

export class Animation {
    constructor(startTime, duration, changeCallback, easing = defaultEasings.cubicOut) {
        this.startTime = startTime;
        this.duration = duration;
        this.changeCallback = changeCallback;
        this.easing = easing;
    }

    setAt(time) {
        this.changeCallback( // update the callback with...
            this.easing( // ...the easing of choice...
                (time - this.startTime) / this.duration // ...of a linear ratio
            )
        );
    }
}
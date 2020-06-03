export class AnimationScheduler {
    constructor(cardEngine) {
        this.cardEngine = cardEngine;
    }

    animateAfter(animation) {
        const lastAnimation = this.cardEngine.animations[this.cardEngine.animations.length - 1];
        if (lastAnimation) {
            animation.startTime = lastAnimation.startTime + lastAnimation.duration;
        } else {
            animation.startTime = this.cardEngine.config.time;
        }
        this.cardEngine.animations.push(animation);
        return this;
    }

    animateWith(animation) {
        const lastAnimation = this.cardEngine.animations[this.cardEngine.animations.length - 1];
        if (lastAnimation) {
            animation.startTime = lastAnimation.startTime;
        } else {
            animation.startTime = this.cardEngine.config.time;
        }
        this.cardEngine.animations.push(animation);
        return this;
    }
}
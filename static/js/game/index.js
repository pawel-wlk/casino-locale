import {
    CardEngine
} from '../modules/CardEngine.js';
import {
    Card,
    defaultColors
} from '../modules/Card.js';
import {
    Animation,
    createDefaultCallback
} from '../modules/Animation.js';
import {
    Token,
    defaultValues
} from '../modules/Token.js';

window.addEventListener('load', () => {
    const engine = new CardEngine(document.querySelector('canvas'));
    const animatedCard = new Card('3', defaultColors.clubs);

    engine.animations.push(
        new Animation(1000, 300,
            createDefaultCallback.position(
                animatedCard, {
                    x: 0,
                    y: 0
                }, {
                    x: 100,
                    y: 100
                }
            )
        ),
        new Animation(2000, 500,
            createDefaultCallback.position(
                animatedCard, {
                    x: 100,
                    y: 100
                }, {
                    x: 200,
                    y: 100
                }
            )
        ),
        new Animation(2500, 1000,
            createDefaultCallback.position(
                animatedCard, {
                    x: 200,
                    y: 100
                }, {
                    x: 100,
                    y: 200
                }
            )
        ),
    );
    engine.objects.push(
        animatedCard,
        new Token(defaultValues[1000])
    );

    function draw(time) {
        requestAnimationFrame(draw);
        engine.draw(time);
    }
    draw(0);
});
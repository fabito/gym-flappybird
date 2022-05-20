
# gym-flappybird

This is an openai gym environment for the HTML5 game: [Flappybird](https://fabito.github.io/flappybird/).

## flappybird-v0

In this environment, the observation is an RGB image of the screen, which is an array of shape (156, 117, 3).

There are only 2 possible actions:

* 0 - Noop
* 1 - Flap

The game is controlled through Pyppeteer (a Puppeteer Python port), which launches instances of the Chromium web browser.

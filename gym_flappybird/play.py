import argparse
from pathlib import Path

from asciimatics.renderers import ColourImageFile, ImageFile
from asciimatics.screen import Screen

from gym_flappybird import SyncFlappyBird


def main(screen, args):
    home_dir = Path.home()
    data_dir = Path(home_dir, 'flappybird')
    data_dir.mkdir(exist_ok=True)

    game = SyncFlappyBird.create(headless=not args.non_headless, user_data_dir=str(data_dir))
    game.load()

    while True:
        state = game.get_state(include_snapshot='bytes')
        ev = screen.get_key()
        if ev in (Screen.KEY_LEFT, ord('A'), ord('a'), Screen.KEY_RIGHT, ord('D'), ord('d')):
            game.tap()
        elif ev in (Screen.KEY_UP, ord('W'), ord('w')):
            game.restart()
        elif ev in (ord('P'), ord('p')):
            if game.is_paused():
                game.resume()
            else:
                game.pause()
        elif ev in (Screen.KEY_ESCAPE, ord('Q'), ord('q')):
            game.stop()
            break

        if args.color:
            renderer = ColourImageFile(screen, state.snapshot, height=args.height)
        else:
            renderer = ImageFile(state.snapshot, height=args.height, colours=screen.colours)

        image, colours = renderer.rendered_text
        for (i, line) in enumerate(image):
            screen.centre(line, i, colour_map=colours[i])
            # screen.paint(line, 0, i, colour_map=colours[i], transparent=False)
        screen.refresh()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--color', action='store_true', default=False, help="Enable colors")
    parser.add_argument('--non-headless', action='store_true', default=False, help="Enable colors")
    parser.add_argument('--height', type=int, default=60, help="Screen height")

    args = parser.parse_args()
    Screen.wrapper(main, arguments=[args])

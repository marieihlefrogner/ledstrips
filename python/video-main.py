import argparse

from video.video_colors import capture_loop
from common.led_controller import init_controller


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-p', '--preview', default=False, action='store_true', help='Enable this to show a preview of the screen')
    parser.add_argument('-v', '--verbose', default=0, action='count', help='Verbosity level')
    parser.add_argument('-m', '--monitor', type=int, default=1, help='Monitor id to capture')
    parser.add_argument('-b', '--brightness', type=float, default=1, help='Float value between 0 and 1 that determines the brightness')
    parser.add_argument('-t', '--threshold', type=int, default=1, help='Do not update color if the difference between the old and new color is below this value')

    args = parser.parse_args()

    init_controller(verbose=args.verbose)
    capture_loop(do_show_screen=args.preview, monitor=args.monitor, brightness=args.brightness, change_threshold=args.threshold, verbose=args.verbose)

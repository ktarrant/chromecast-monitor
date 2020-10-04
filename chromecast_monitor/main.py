"""
Example showing how to create a simple Chromecast event listener for
device and media status events
"""

import argparse
import logging
import sys
import time

import pychromecast
import zeroconf


FORMAT = "%(asctime)s [%(name)s %(levelname)s] %(message)s"


class StatusListener:
    def __init__(self, name, cast):
        self.logger = logging.getLogger(f"{name}.status")
        self.cast = cast

    def new_cast_status(self, status):
        self.logger.info(f"status change: {status}")


class StatusMediaListener:
    def __init__(self, name, cast):
        self.logger = logging.getLogger(f"{name}.media")
        self.cast = cast

    def new_media_status(self, status):
        self.logger.info(f"media change: {status}")


parser = argparse.ArgumentParser(
    description=" Listens to the list of chromecasts provided and logs all media and status changes to a file"
)
parser.add_argument('chromecasts', nargs='*', help='List of friendly names of chromecasts to listen to')
parser.add_argument("--file", help="Output log file name", default="chromecast_monitor.log")
parser.add_argument("--show-debug", help="Enable debug log", action="store_true")
parser.add_argument(
    "--show-zeroconf-debug", help="Enable zeroconf debug log", action="store_true"
)
args = parser.parse_args()

if not args.chromecasts:
    print("No chromecasts provided.")
    sys.exit(1)

logger = logging.getLogger("chromecast_monitor")
log_level = logging.DEBUG if args.show_debug else logging.INFO
stream_handler = logging.StreamHandler()
# stream_handler.setLevel(log_level)
file_handler = logging.FileHandler(args.file)
# file_handler.setLevel(log_level)
logging.basicConfig(level=log_level,
                    format=FORMAT,
                    handlers=[stream_handler, file_handler])
if args.show_zeroconf_debug:
    logger.debug("Zeroconf version: " + zeroconf.__version__)
    logging.getLogger("zeroconf").setLevel(logging.DEBUG)

chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=args.chromecasts)
if not chromecasts:
    logger.fatal('No chromecast with name "{}" discovered'.format(args.cast))
    sys.exit(1)

for chromecast in chromecasts:
    # Start socket client's worker thread and wait for initial status update
    chromecast.wait()

    listenerCast = StatusListener(chromecast.name, chromecast)
    chromecast.register_status_listener(listenerCast)

    listenerMedia = StatusMediaListener(chromecast.name, chromecast)
    chromecast.media_controller.register_status_listener(listenerMedia)

input("Listening for Chromecast events...\n\n")

# Shut down discovery
pychromecast.discovery.stop_discovery(browser)

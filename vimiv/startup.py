# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Functions called at startup before the Qt main loop."""

import argparse
import logging
import logging.handlers
import os

import vimiv
from vimiv import app
from vimiv.commands import argtypes
from vimiv.config import configfile, keyfile, settings
from vimiv.gui import mainwindow
from vimiv.utils import xdg


def run(argv):
    """Run the functions to set up everything.

    Args:
        argv: sys.argv[1:] from the executable.
    """
    # Setup directories
    init_directories()
    # Parse args
    parser = get_argparser()
    args = parser.parse_args(argv)
    # Setup logging
    setup_logging(args.log_level)
    logging.info("Start: vimiv %s", " ".join(argv))
    # Parse settings
    settings.init_defaults()
    configfile.parse(args)
    keyfile.parse(args)
    update_settings(args)
    # Set up UI
    init_ui(args)
    # Open paths
    app.open(args.paths)
    # Finalize
    logging.info("Startup completed")


def setup_logging(log_level):
    """Prepare the python logging module.

    Sets it up to write to stderr and $XDG_DATA_HOME/vimiv/vimiv.log.

    Args:
        log_level: Log level as string as given from the command line.
    """
    log_format = logging.Formatter(
        "[%(asctime)s] %(levelname)s: %(message)s", datefmt="%H:%M:%S")
    logger = logging.getLogger()
    logger.setLevel(log_level)

    file_handler = logging.FileHandler(
        xdg.join_vimiv_data("vimiv.log"), mode="w")
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)


def get_argparser():
    """Get the argparse parser."""
    parser = argparse.ArgumentParser(prog=vimiv.__name__,
                                     description=vimiv.__description__)
    parser.add_argument("-f", "--fullscreen", action="store_true",
                        help="Start fullscreen")
    parser.add_argument("-v", "--version", action="version",
                        version="vimiv version %s" % vimiv.__version__,
                        help="Print version information and exit")
    parser.add_argument("--slideshow", action="store_true",
                        help="Start slideshow at start-up")
    parser.add_argument("-g", "--geometry", type=argtypes.geometry,
                        metavar="WIDTHxHEIGHT",
                        help="Set the starting geometry")
    parser.add_argument("--temp-basedir", action="store_true",
                        help="Use a temporary basedir")
    parser.add_argument("--config", type=argtypes.existing_file,
                        metavar="FILE",
                        help="Use FILE as local configuration file")
    parser.add_argument("--keyfile", type=argtypes.existing_file,
                        metavar="FILE", help="Use FILE as keybinding file")
    parser.add_argument("-s", "--set", nargs=2, default=[], action="append",
                        dest="cmd_settings", metavar=("OPTION", "VALUE"),
                        help="Set a temporary setting")
    # parser.add_argument("--debug", action="store_true",
    #                     help="Run in debug mode")
    parser.add_argument("--log-level", type=argtypes.loglevel, metavar="LEVEL",
                        help="Set log level to LEVEL", default="warning")
    parser.add_argument("paths", nargs="*", type=argtypes.existing_path,
                        metavar="PATH", help="Paths to open")
    return parser


def init_directories():
    """Create vimiv cache, config and data directories."""
    for directory in [xdg.get_vimiv_cache_dir(),
                      xdg.get_vimiv_config_dir(),
                      xdg.get_vimiv_data_dir()]:
        if not os.path.isdir(directory):
            os.mkdir(directory)


def init_ui(args):
    """Initialize the Qt UI."""
    mw = mainwindow.MainWindow()
    if args.fullscreen:
        mw.fullscreen()
    mw.show()


def update_settings(args):
    """Update settings in storage with arguments from command line.

    Args:
        args: Arguments returned from parser.parse_args().
    """
    for pair in args.cmd_settings:
        option = pair[0]
        value = pair[1]
        settings.override(option, value)
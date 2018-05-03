"""Common utils."""
import logging
import sys


def init_logging():
    """Initialize the logging """
    logging.root.setLevel(logging.DEBUG)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    logging.root.addHandler(stdout_handler)

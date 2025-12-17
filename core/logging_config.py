import logging
import sys


def setup_logging(log_level: str = "INFO"):
    logging.basicConfig(
        level=log_level,
        format=(
            "%(asctime)s | %(levelname)-8s | "
            "%(name)s | %(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

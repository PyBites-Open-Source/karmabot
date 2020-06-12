import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",  # noqa E501
    datefmt="%m-%d %H:%M",
    handlers=[logging.StreamHandler()],
)

logging.info("Script started")

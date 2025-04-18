from logging import INFO

from decouple import config

config.search_path = "./docker"


DEBUG=False
LOGGER_LEVEL= INFO

if config("DEBUG"):
    DEBUG=config("DEBUG")
    LOGGER_LEVEL=10

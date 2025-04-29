from logging import INFO

from decouple import config

config.search_path = "./docker"


DEBUG=False
LOGGER_LEVEL= INFO

if config("DEBUG"):
    DEBUG=config("DEBUG")
    LOGGER_LEVEL=10

MONGO_READER_URI = config("MONGO_READER_URI")
MONGO_DB = config("MONGO_DB")
MONGO_COLLECTION = config("MONGO_COLLECTION")
MONGO_POOL_SIZE = (config("MONGO_POOL_MIN_SIZE"), config("MONGO_POOL_MAX_SIZE"))


POSTGRES_HOST=config("POSTGRES_HOST")
POSTGRES_DB=config("POSTGRES_DB")

POSTGRES_USER=config("POSTGRES_USER")
POSTGRES_PASSWORD=config("POSTGRES_PASSWORD")

POOL_SIZE = 10

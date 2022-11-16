import logging
import time

import backoff
import extractor
import loader
import state_
import transformer
import utils
from settings import APP_CONFIG, BACKOFF_CONFIG

logging.basicConfig(
    level=logging.DEBUG if APP_CONFIG.debug else logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)
logging.getLogger("backoff").addHandler(logging.StreamHandler())


@backoff.on_exception(**BACKOFF_CONFIG)
def etl(state: state_.State) -> None:
    """Run main ETL routine.

    Process records in chunks by size, defined in settings. After successful run
    of this function all non-updated records should be updated.

    Args:
        state: Persistent state storage.
    """
    timestamp = state.get_value(APP_CONFIG.es_index_name)
    records_generator = extractor.extract_postgres(timestamp)
    documents_generator = transformer.transform(records_generator)
    loader.load_elastic(state, documents_generator)


def main():
    """Make setup and run ETL itself.

    Uses backoff to restart on certain exceptions.
    """
    # create State instance once at beginning of process
    storage = state_.JsonFileStorage(APP_CONFIG.json_storage_path)
    state = state_.State(storage)

    while True:
        logger.debug("Start ETL round")
        etl(state)
        time.sleep(APP_CONFIG.etl_interval)


if __name__ == "__main__":
    utils.create_elasticsearch_index(APP_CONFIG.es_index_name)
    main()

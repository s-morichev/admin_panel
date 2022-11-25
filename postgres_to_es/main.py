import logging
import time

import backoff

import postgres_to_es.extractor
import postgres_to_es.loader
import postgres_to_es.logging_config
import postgres_to_es.state_
import postgres_to_es.transformer
import postgres_to_es.utils
from postgres_to_es.settings import APP_CONFIG, BACKOFF_CONFIG

logger = logging.getLogger(__name__)


@backoff.on_exception(**BACKOFF_CONFIG)
def etl(state: postgres_to_es.state_.State) -> None:
    """Run main ETL routine.

    Process records in chunks by size, defined in settings. After successful run
    of this function all non-updated records should be updated.

    Args:
        state: Persistent state storage.
    """
    timestamp = state.get_value(APP_CONFIG.es_index_name)
    records_generator = postgres_to_es.extractor.extract_postgres(timestamp)
    documents_generator = postgres_to_es.transformer.transform(records_generator)
    postgres_to_es.loader.load_elastic(state, documents_generator)


def main():
    """Make setup and run ETL itself.

    Uses backoff to restart on certain exceptions.
    """
    # create State instance once at beginning of process
    storage = postgres_to_es.state_.JsonFileStorage(APP_CONFIG.json_storage_path)
    state = postgres_to_es.state_.State(storage)

    while True:
        logger.debug("Start ETL round")
        etl(state)
        time.sleep(APP_CONFIG.etl_interval)


if __name__ == "__main__":
    postgres_to_es.logging_config.setup_logging()
    postgres_to_es.utils.create_elasticsearch_index(APP_CONFIG.es_index_name)
    main()

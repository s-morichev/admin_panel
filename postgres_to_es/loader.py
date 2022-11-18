import datetime
import logging
from contextlib import closing
from typing import Any, Iterator

import backoff
import state_
import utils
from elasticsearch import helpers
from settings import APP_CONFIG, BACKOFF_CONFIG

logger = logging.getLogger(__name__)

ESActions = Iterator[dict[str, Any]]

DELTA = datetime.timedelta(milliseconds=1)


@backoff.on_exception(**BACKOFF_CONFIG)
def _load_bulk(actions: ESActions) -> int:
    """Bulk load chunk of documents into Elasticsearch.

    Uses backoff to wait until successful loading.

    Args:
        actions: A iterator of documents to load.

    Returns:
        Number of loaded documents
    """
    with closing(utils.get_elasticsearch_client()) as es:
        successes, _ = helpers.bulk(
            client=es,
            actions=actions,
            chunk_size=APP_CONFIG.chunk_size,
        )
    return successes


def load_elastic(
    state: state_.State,
    documents_generator: Iterator[tuple[ESActions, datetime.datetime]],
) -> None:
    """Load documents into elasticsearch.

    Load documents in bulk. Entire bulk is either loaded or not. In case of
    errors in documents generator the function aborts in order prevent data loss.

    Args:
        state: Persistent state storage.
        documents_generator: An iterator containing generator of documents and
            datetime to save in case of successful loading.
    """
    # There could be a lot of documents with same datetime so save a little lower
    # datetime for each chunk. If there was error in document generator then
    # ETL would restart from that lower datetime and re pickup documents with same
    # datetime. As for documents with different datetime, if there was error then
    # ETL would re pickup only documents that were modified in small interval.
    last_modified = None
    for actions, last_modified in documents_generator:
        loaded = _load_bulk(actions)
        state.set_value(APP_CONFIG.es_index_name, (last_modified - DELTA).isoformat())
        logger.info("Loaded %s documents into elasticsearch", loaded)

    # Save actual datetime after loading of all chunks
    if last_modified is not None:
        state.set_value(APP_CONFIG.es_index_name, last_modified.isoformat())

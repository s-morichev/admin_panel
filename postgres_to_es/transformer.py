import datetime
from typing import Any, Iterator

import models
from settings import APP_CONFIG

ESActions = Iterator[dict[str, Any]]


def transform(
    models_generator: Iterator[tuple[models.MovieDocument]],
) -> Iterator[tuple[ESActions, datetime.datetime]]:
    """Transform pydantic models into elasticsearch documents.

    Args:
        models_generator: An iterator of tuples, containing pydantic models
            to transform.

    Yields:
        Tuple consisting of generator of elasticsearch documents and datetime
        of modification of last document in that generator.
    """
    for models_tuple in models_generator:
        last_modified = models_tuple[-1].modified
        actions = (
            {
                "_index": APP_CONFIG.es_index_name,
                "_id": model.id,
                "_source": model.dict(exclude={"modified"}),
            }
            for model in models_tuple
        )
        yield actions, last_modified

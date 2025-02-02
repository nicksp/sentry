from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, MutableMapping, Optional

from django.conf import settings


class UseCaseKey(Enum):
    RELEASE_HEALTH = "release-health"
    PERFORMANCE = "performance"

    @staticmethod
    def from_str(use_case: str) -> "UseCaseKey":
        if use_case == "performance":
            return UseCaseKey.PERFORMANCE
        elif use_case in ("release-health", "releaseHealth"):
            return UseCaseKey.RELEASE_HEALTH
        else:
            raise ValueError


class DbKey(Enum):
    STRING_INDEXER = "StringIndexer"
    PERF_STRING_INDEXER = "PerfStringIndexer"


@dataclass(frozen=True)
class MetricsIngestConfiguration:
    db_model: DbKey
    input_topic: str
    output_topic: str
    use_case_id: UseCaseKey
    internal_metrics_tag: Optional[str]
    writes_limiter_cluster_options: Mapping[str, Any]


_METRICS_INGEST_CONFIG_BY_USE_CASE: MutableMapping[UseCaseKey, MetricsIngestConfiguration] = dict()


def _register_ingest_config(config: MetricsIngestConfiguration) -> None:
    _METRICS_INGEST_CONFIG_BY_USE_CASE[config.use_case_id] = config


_register_ingest_config(
    MetricsIngestConfiguration(
        db_model=DbKey.STRING_INDEXER,
        input_topic=settings.KAFKA_INGEST_METRICS,
        output_topic=settings.KAFKA_SNUBA_METRICS,
        use_case_id=UseCaseKey.RELEASE_HEALTH,
        internal_metrics_tag="release-health",
        writes_limiter_cluster_options=settings.SENTRY_METRICS_INDEXER_WRITES_LIMITER_OPTIONS,
    )
)
_register_ingest_config(
    MetricsIngestConfiguration(
        db_model=DbKey.PERF_STRING_INDEXER,
        input_topic=settings.KAFKA_INGEST_PERFORMANCE_METRICS,
        output_topic=settings.KAFKA_SNUBA_GENERIC_METRICS,
        use_case_id=UseCaseKey.PERFORMANCE,
        internal_metrics_tag="perf",
        writes_limiter_cluster_options=settings.SENTRY_METRICS_INDEXER_WRITES_LIMITER_OPTIONS_PERFORMANCE,
    )
)


def get_ingest_config(use_case_key: UseCaseKey) -> MetricsIngestConfiguration:
    return _METRICS_INGEST_CONFIG_BY_USE_CASE[use_case_key]

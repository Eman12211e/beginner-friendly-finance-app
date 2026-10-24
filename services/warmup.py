# Owner: Agent E. W0 created this stub.
import logging

import config

log = logging.getLogger(__name__)


def run_if_enabled(app) -> None:
    log.info("warmup not built yet" if config.WARM_CACHE else "warmup disabled")

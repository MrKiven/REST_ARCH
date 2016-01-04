# -*- coding: utf-8 -*-

import logging

logger = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(
    logging.Formatter('[SKT %(levelname)-7s] %(message)s')
)
logger.addHandler(console)
logger.setLevel(logging.INFO)

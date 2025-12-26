#!/bin/bash

python -m metric.run --input data/sample.csv \
--output data/v2/out_sample.jsonl \
--config metric/config/default.yaml \
--workers 2
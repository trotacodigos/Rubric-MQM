#!/bin/bash

export PYTHONPATH=$(pwd)
savedir="data"

python3 -m evaluator.worker -d $savedir/sample.csv \
                            -o $savedir/out.csv \
                            -e $savedir/error.jsonl \
                            -m "gpt-3.5-turbo"
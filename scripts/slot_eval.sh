#!/bin/bash

export PYTHONPATH=$(pwd)
savedir="data"
python3 -m evaluator.slot_scenarios.subworker -d $savedir/sample.csv \
                                              -o $savedir/output_slot.csv \
                                              -e $savedir/error_slot.jsonl \
                                              -p \
                                              -s deepsqm \
                                              -c 8
                  
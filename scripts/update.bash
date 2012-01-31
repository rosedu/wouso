#!/bin/bash
# scoring update script

HERE=`dirname $0`/..

export PYTHONPATH=$HERE:$HERE/wouso/:$PYTHONPATH

python $HERE/wouso/utils/scoring_update.py


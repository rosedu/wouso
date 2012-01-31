#!/bin/bash
# EOT script, cron friendly

HERE=`dirname $0`/..

export PYTHONPATH=$HERE:$HERE/wouso/:$PYTHONPATH

python $HERE/wouso/utils/eot_top_update.py


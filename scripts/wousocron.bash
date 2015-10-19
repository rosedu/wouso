#!/bin/bash
# crontab script, cron friendly
# to be run hourly, example: "0 * * * *"

HERE=`dirname $0`/..

export PYTHONPATH=$HERE:$HERE/wouso/:$PYTHONPATH

python $HERE/wouso/manage.py wousocron >> ../log/wousocron.log 2>&1

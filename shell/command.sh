#!/bin/bash
export PYTHONIOENCODING=utf-8
export DJANGO_SETTINGS_MODULE=logue.settings
. /Users/kita83/.virtualenvs/env2/bin/activate
cd /Users/kita83/work/logue
python3 manage.py poll_feeds --verbose

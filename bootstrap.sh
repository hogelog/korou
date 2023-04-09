#!/bin/sh

sh -c "$BOOTSTRAP_COMMAND"

python slack_command.py

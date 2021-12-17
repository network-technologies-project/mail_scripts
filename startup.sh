#!/bin/bash

pwd > /home/mikhail/git/mail_scripts/tmp.txt
rm /home/mikhail/git/mail_scripts/tmp.txt
python2 /home/mikhail/moin/moin-1.9.11/wikiserver.py > /dev/null 2>&1 &
sleep 10
disown
ngrok http 8080 --log=stdout > /home/mikhail/git/mail_scripts/tmp.txt &
disown

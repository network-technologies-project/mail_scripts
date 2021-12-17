#!/bin/bash

rm /home/mikhail/git/mail_scripts/info.txt
grep url= /home/mikhail/git/mail_scripts/tmp.txt > /home/mikhail/git/mail_scripts/info.txt
python3 /home/mikhail/git/mail_scripts/message_script.py
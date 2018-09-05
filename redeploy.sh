#!/bin/bash
kill -9 $(ps -ef |grep run.sh|grep -v grep|perl -pe 's/\S+\s+(\S+).*/\1/g' 2>/dev/null)
kill -9 $(ps -ef |grep " main.py"|grep -v grep|perl -pe 's/\S+\s+(\S+).*/\1/g' 2>/dev/null)
cd $HOME/code/karmabot && nohup ./run.sh &

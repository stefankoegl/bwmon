#!/bin/bash

while [ 1 ]
do
    DATE=`date +%T`
    MEM=`ps ax -o rss,command | grep runmonitor | grep -v grep | awk '{ print $1 }'`
    echo $DATE $MEM
    sleep 1
done


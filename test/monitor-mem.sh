#!/bin/bash

while [ 1 ]
do
    date +%T
    ps ax -o rss,command | grep runmonitor | grep -v grep
    sleep 1
done


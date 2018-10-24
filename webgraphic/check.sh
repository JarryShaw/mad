#!/bin/bash

grep="grep --color=auto"

FILE="07241715.out"

ps -aux | $grep mad

head -n 1 $FILE

$grep "No\." $FILE | tail -5 | $grep "No\."

# $grep "@" $FILE | tail | $grep "@"

tail -5 $FILE ; echo

$grep "loss\:" $FILE | tail -5 | $grep "loss\:"

$grep Traceback $FILE -c

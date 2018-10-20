#!/bin/sh
tuning="${5}"
time ./tune.py "${1}" "${2}" "${3}" "${4}" $tuning
sox -t raw -r "${1}" -b "${2}" -c 2 -e signed-integer $tuning.raw $tuning.wav
#play tune.wav


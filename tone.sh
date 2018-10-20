#!/bin/sh
time ./tone.py "${1}" "${2}" "${3}" "${4}" > tone.raw
sox -t raw -r "${1}" -b "${2}" -c 2 -e signed-integer tone.raw tone.wav
#play tone.wav


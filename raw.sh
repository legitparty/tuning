#!/bin/sh
if [ "${1}" ]
then
	rate="${1}"
else
	rate=44100
fi
echo -t raw -r "${rate}" -b 16 -c 2 -e signed-integer

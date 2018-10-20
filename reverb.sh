#!/bin/sh
if [ "${1}" ]
then
	wet="${1}"
else
	wet=-4
fi
echo pad 0 5 reverb 80 20 100 100 0 "${wet}"

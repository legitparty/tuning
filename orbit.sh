#!/bin/sh
tail -f -n +3 orbit.txt | awk 'BEGIN {print "scale=30"} {if ($2 > 0) { print "12 * "$2" / "$1; fflush()} }' | bc 

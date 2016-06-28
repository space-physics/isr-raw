#!/bin/sh
# collects directory of PNGs into lossless MKV FFV1 video

cd /tmp/20*

~/code/pybashutils/ren.sh "*.png"

ffmpeg -framerate 5 -pattern_type glob -i "*.png" -c:v ffv1 ~/Dropbox/aurora_data/StudyEvents/2013-04-14/out.mkv


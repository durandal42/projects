#!/bin/bash

set -e

mkdir -p movies

echo 'combining images into movie...'
ffmpeg -r 30 -i images/${1}/%d.png -vcodec h264 -y -pix_fmt yuv420p movies/${1}.mp4

echo 'cleaning up' images/${1}/
rm -rf images/${1}/

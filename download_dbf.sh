#!/bin/bash

for ((i=2016;i<=2021;i++)); do
  for ((j=1;j<=12;j++)); do
    if [ $j -lt 10 ]; then
      k=0"$j"
    else
      k=$j
    fi
    filename=https://www.cbr.ru/vfs/statistics/pdko/f316/316-"$i""$k"01.rar
    wget "$filename" -O file.rar
    unar -f file.rar PI_316*
  done
done
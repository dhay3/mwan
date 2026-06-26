#!/usr/bin/env bash

size_info=$(dmidecode -t memory | grep '^\s*Size' | grep -v No | head -1 | awk '{print $2}')
Locator=$(dmidecode -t memory | grep -C 5 $size_info | grep '^\s*Locator' | awk -F ':' '{print $2}')
crc_info=$(grep "[0-9]" /sys/devices/system/edac/mc/mc*/csrow*/ch*_ce_count 2> /dev/null || grep "[0-9]" /sys/devices/system/edac/mc/mc*/dimm*/dimm_ce_count 2> /dev/null)

IFS=$'\n' read -rd '' -a Mfrs_array <<< "$Locator"
IFS=$'\n' read -rd '' -a crc_array <<< "$crc_info"

if [ ${#crc_array[@]} == ${#Mfrs_array[@]} ]; then
  declare -A array
  for i in ${!crc_array[@]}; do
    array[${crc_array[$i]}]=${Mfrs_array[$i]}
  done
  for i in ${!array[@]}; do
    crc_err=$(echo $i | cut -d ":" -f 2)
    if [ $crc_err -gt 0 ]; then
      echo "内存异常,插槽:${array[$i]},错误数:${crc_err};"
    fi
  done
else
  diff=$((${#crc_array[@]} - ${#Mfrs_array[@]}))
  echo "内存数量异常,掉内存数:$diff"
fi

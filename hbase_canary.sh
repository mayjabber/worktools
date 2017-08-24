#!/bin/sh
POINT=1

DEBUG=1

return_code=1
max_ms=0

old_IFS=$IFS
IFS=$'\n'
for line in `hbase org.apache.hadoop.hbase.tool.Canary 2>&1|grep region`;
do
    ms=`echo $line|sed -n 's/.*in \([0-9]*\)ms$/\1/p'`

    if [[ $ms -gt $max_ms ]];then
        max_ms=$ms
    fi

    if [[ $ms -eq '' ]];then
        if [[ $DEBUG -ne 0 ]];then
            echo $line >&2
        fi
        echo 10000
        exit 1
    fi

    if [[ $ms -gt $POINT ]];then
        if [[ $DEBUG -ne 0 ]];then
            echo $line >&2
        fi
        echo $ms
        exit 1
    else
        return_code=0
    fi
done
IFS=$old_IFS

echo $max_ms
exit $return_code

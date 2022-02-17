#!/bin/bash

WAIT_FOR_IT() {
    echo "Pressione qualquer tecla para matar os processos"
    while [ true ] ; do
        read -t 3 -n 1
        if [ $? = 0 ] ; then
            return ;
        else
            echo "..."
        fi
    done
}

M=$1
serversNum=$2
maxNodes=$(echo "2^$M" | bc)

echo "Subira $serversNum servidores numa rede que usara $M bits para a hash"

declare -A serverPids
for i in $(seq 1 $serversNum); do
    N=$(echo $(($RANDOM % $maxNodes)))
    echo "$N"

    python3 Server.py $N $M &
    export serverPid=$!
    serverPids[$i]=$serverPid
done

echo "pids dos servidores: ${serverPids}, ${serverPids[2]}"

WAIT_FOR_IT

for i in $(seq 1 $serversNum); do
    kill -SIGUSR1 ${serverPids[$i]}
done

WAIT_FOR_IT

for i in $(seq 1 $serversNum); do
    kill -9 ${serverPids[$i]}
done

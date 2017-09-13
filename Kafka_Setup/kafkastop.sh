#!/bin/sh
# Stop kafka server and zookeeper

~/opt/kafka_2.12-0.10.2.0/bin/kafka-server-stop.sh ~/opt/kafka_2.12-0.10.2.0/config/server.properties &

sleep 3

~/opt/kafka_2.12-0.10.2.0/bin/zookeeper-server-stop.sh ~/opt/kafka_2.12-0.10.2.0/config/zookeeper.properties &

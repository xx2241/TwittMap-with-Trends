#!/bin/sh
# Start zookeeper and kafka server

~/opt/kafka_2.12-0.10.2.0/bin/zookeeper-server-start.sh ~/opt/kafka_2.12-0.10.2.0/config/zookeeper.properties &

sleep 3

~/opt/kafka_2.12-0.10.2.0/bin/kafka-server-start.sh ~/opt/kafka_2.12-0.10.2.0/config/server.properties &

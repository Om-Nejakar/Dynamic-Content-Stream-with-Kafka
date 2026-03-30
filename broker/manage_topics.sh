#list all topics
bin/kafka-topics.sh --list --bootstrap-server 192.168.196.62:9092

#describe a topic
/opt/kafka/bin/kafka-topics.sh --describe --topic <topic_name> --bootstrap-server 192.168.196.62:9092

#consume messages from a topic
bin/kafka-console-consumer.sh --bootstrap-server 192.168.196.62:9092 --topic <topic_name> --from-beginning


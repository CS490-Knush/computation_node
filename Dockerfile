#This is a sample Image 
FROM ubuntu 
MAINTAINER anushree.agrawal@yale.edu

RUN apt-get update && apt-get -y install curl && apt-get install iperf
RUN apt-get install default-jdk
RUN apt-get install scala
RUN apt-get install git
RUN wget https://www.apache.org/dyn/closer.lua/spark/spark-2.4.0/spark-2.4.0-bin-hadoop2.7.tgz && tar xvf spark-2.4.0-bin-hadoop2.7.tgz
CMD ["./spark-2.4.0-bin-hadoop2.7/bin/spark-shell"]

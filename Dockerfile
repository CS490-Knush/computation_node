#This is a sample Image 
FROM knush/spark-server 
MAINTAINER anushree.agrawal@yale.edu

WORKDIR /computation_node

EXPOSE 80 22
CMD ["python3", "app.py"]

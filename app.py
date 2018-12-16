from flask import Flask, request, Response
import os
import socket
import time
import subprocess
from multiprocessing import Process
import requests
import datetime

app = Flask(__name__)

storage_node = None
bandwidth = None
csv_file_name = None

@app.route("/")
def hello():
    html = "<h3>Hello {name}!</h3>" \
           "<b>Hostname:</b> bla<br/>"
    return html.format(name="friend")

@app.route("/tc", methods=["POST"])
def tc():
    tc_data = request.json
    global storage_node
    global bandwidth
    global csv_file_name
    bandwidth = tc_data['bandwidth']
    # do the tc -> kshia
    p = subprocess.call("pwd")
    p = subprocess.call("ls")
    p = subprocess.call("./tc_bw_limit.sh %s" % str(bandwidth), shell=True)
    # set storage_node
    storage_node = tc_data['storage_ip']
    csv_file_name = '{id}_{date:%Y-%m-%d_%H-%M-%S}.dat'.format(id=socket.gethostname(), date=datetime.datetime.now())
    return Response("Successfully configured tc", status=200)

@app.route("/run_job", methods=["POST"])
def run_job():
    job = request.json
    data_file = job['data_file']
    spark_program = job['spark_program']
    start_time = time.time()

    print("Starting to run spark program %s with file %s" % (spark_program, data_file))
    r = requests.get("http://%s/get_data_file/%s" % (storage_node, data_file))

    file_time = time.time() - start_time
    print(r.content)
    file_size = len(r.content)
    with open("fetched/%s" % data_file, 'wb') as f:
        f.write(r.content)
    # r = subprocess.Popen(["scp", "root@%s:/%s" % (storage_node, data_file), "."])
    p = Process(target=run_spark_job, args=(spark_program, data_file))
    p.start()
    p.join()

    end_time = time.time()
    total_time = end_time - start_time
    job_time = end_time - file_time

    print("Finished running spark job %s with file %s" % (spark_program, data_file))
    print("Time: %d" % end_time-start_time)
    write_to_csv(file_size=file_size, bandwidth=bandwidth, computation_node=socket.gethostname(), storage_node=storage_node, file_time=file_time, job_time=job_time, total_time=total_time)
    return Response("Success!", status=200)

def write_to_csv(file_size, bandwidth, computation_node, storage_node, file_time, job_time, total_time):
    with open(csv_file_name, 'a') as f:
        f.write("%s,%s,%s,%s,%s,%s,%s,%s" % (str(time.time()), str(file_size), str(bandwidth), str(computation_node), storage_node, str(file_time), str(job_time), str(total_time))

@app.route("/get_data_file/<filename>", methods=["GET"])
def get_data_file(filename):
    return app.send_static_file(filename)

def run_spark_job(spark_program, data_file):
    try:
        s = subprocess.check_output(['../spark/bin/spark-submit', '--master', 'local', spark_program, data_file])
    except subprocess.CalledProcessError as e:
        raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
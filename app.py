from flask import Flask, request, Response
import os
import socket
import time
import subprocess
from multiprocessing import Process

app = Flask(__name__)

storage_node = None

@app.route("/")
def hello():
    html = "<h3>Hello {name}!</h3>" \
           "<b>Hostname:</b> bla<br/>"
    return html.format(name="friend")

@app.route("/tc", methods=["POST"])
def tc():
    tc_data = request.json
    global storage_node
    bandwidth = tc_data['bandwidth']
    # do the tc -> kshia
    p = subprocess.call("./tc_bw_limit.sh %s", str(bandwidth))
    # set storage_node
    storage_node = tc_data['storage_ip']
    return Response("Successfully configured tc", status=200)

@app.route("/run_job", methods=["POST"])
def run_job():
    job = request.json
    data_file = job['data_file']
    spark_program = job['spark_program']
    curr_time = time.time()
    print("Starting to run spark program %s with file %s" % (spark_program, data_file))
    p = subprocess.Popen(["scp", "root@%s:/%s" % (storage_node, data_file), "."])
    sts = p.wait()
    if sts is not 0:
        # failure
        return Response("File transfer did not work", status=400)
    p = Process(target=run_spark_job, args=(spark_program, data_file))
    p.join()
    end_time = time.time()
    print("Finished running spark job %s with file %s" % (spark_program, data_file))
    print("Time: %d" % end_time-start_time)
    return Response("Success!", status=200)

def run_spark_job(spark_program, data_file):
    try:
        s = subprocess.check_output(['../spark/bin/spark-submit', '--master', 'local', spark_program, data_file])
    except subprocess.CalledProcessError as e:
        raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
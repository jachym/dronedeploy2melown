from flask import Flask
from flask import request
import os
import json

app = Flask(__name__)

def get_outfile():

    dirname = os.path.dirname(__file__)
    outdir = os.path.join(dirname, "..", "..", "LogFiles", "http", "RawLogs", "out")
    if not os.path.isdir(outdir):
        os.mkdir(outdir)
    outfile = os.path.join(outdir, "out.txt")
    return outfile

def writeout(data, mode="w"):

    outfile = get_outfile()

    with open(outfile, mode) as out:
        out.write(data)

@app.route('/', methods=["POST", "GET"])
def hello_world():

    if request.method == "POST":
        pass


    #print(request.args)
    #print(request.method)
    #print(request.headers["Content-type"])
    #writeout("{}".format(request.headers["Content-type"], "w"))
    #return("Hello world agin")
    #
    #if request.headers['Content-Type'] == 'text/plain':
    #    try:
    #        writeout(request.data, "wb")
    #    except Exception as e:
    #        writeout(str(e), "w")
    #
    #elif request.headers['Content-Type'] == 'application/json':
    #    writeout(json.dumps(request.json), "w")
    #
    #elif request.headers['Content-Type'] == 'application/octet-stream':
    #    writeout(request.data, "wb")
    #
    #else:
    #    writeout("415 Unsupported Media Type ;) {}".format(request.headers["Content-type"]), "w")

    outfile = get_outfile()
    with open(outfile, "w") as out:
        out.write(str(request.headers))
        out.write("\n---------------------\n")
        if hasattr(request, "data"):
            out.write(str(request.data))
            out.write("\n---------------------\n")
        if hasattr(request, "args"):
            out.write(str(request.args))
            pass


    return "hello"
    #return 'Hello, World! {} {}'.format(outdir, outfile)

if __name__ == '__main__':
  app.run()

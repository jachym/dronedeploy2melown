from flask import Flask
from flask import request
import os
import json
import atexit
import shutil
import tempfile
import requests
import zipfile

app = Flask(__name__)
app.debug = True
TEMPDIR = None

def clear():
    global TEMPDIR

    if TEMPDIR and os.path.isdir(TEMPDIR):
        shutil.rmtree(TEMPDIR)

atexit.register(clear)

def get_outfile():

    dirname = os.path.dirname(__file__)
    if os.name != "posix":
        outdir = os.path.join(dirname, "..", "..", "LogFiles", "http", "RawLogs", "out")
    else:
        outdir = "/tmp/"
    if not os.path.isdir(outdir):
        os.mkdir(outdir)
    outfile = os.path.join(outdir, "out.txt")
    return outfile

def writeout(data, mode="w"):

    outfile = get_outfile()

    with open(outfile, mode) as out:
        out.write(data)

def unzip_dataset(url):
    global TEMPDIR

    TEMPDIR = tempfile.mkdtemp(prefix="dronedeploy-")
    r = requests.get(url)
    zip_file = os.path.join(TEMPDIR, "output.zip")
    with open(zip_file, "wb") as out_zip:
        out_zip.write(r.content)

    zf = zipfile.ZipFile(zip_file)
    zf.extractall(TEMPDIR)

    file_name = None
    for f in os.listdir(TEMPDIR):
        if f.endswith(".tif"):
            file_name = os.path.abspath(os.path.join(TEMPDIR, f))
    assert file_name
    return file_name

def send_files(url, data, filename):
    with open(filename, "rb") as tiff_data:
        request = {
            'qqfile': tiff_data,
            'path': data["body"]["files"][0]["path"]
        }
        r = requests.post(url, files=request)
        assert r.status_code == 200

@app.route("/auth", methods=["POST", "GET"])
def myauth():

    html_page = """
    <html>
    <head>
        <script type="text/javascript">
        var receiveMessage = function(event) {

            console.log("ziju!")
            document.write("ziju!")

            var data = {
                access_token: "%s",
                expires: "%s",
                state: "%s",
                action: "%s"
            };
            event.source.postMessage(JSON.stringify(data), event.origin);
            document.write(event.origin);

        };
        window.addEventListener("message", receiveMessage, false);
        document.write("listening");
        </script>
    </head>
    </html>
    """ % (request.args["access_token"], request.args["expires"],
           request.args["state"], request.args["action"])

    response = app.response_class(
        response=html_page,
        status=200,
        mimetype='text/html'
    )
    return response

@app.route('/', methods=["POST", "GET"])
def test():
    return "A life!"

@app.route('/export_mosaic', methods=["POST", "GET"])
def myexport_mosaic():

    outfile = get_outfile()
    data = request.get_json()
    args = request.args

    tif_file = unzip_dataset(data["download_path"])

    url = "https://www.melown.com/cloud/backend/api/account/{}/dataset?app_id={}&access_token={}&req_scopes=MARIO_API".format(args["account_id"], args["app_id"], args["access_token"])

    dataset_name = "{}-{}".format(data["layer"], data["map_id"])
    post_data = {
        "files": [{
          "byte_size": os.stat(tif_file).st_size,
          "crc": "EPSG:3857",
          "path_component": os.path.basename(tif_file)
        }],
        "name": dataset_name,
        "type": "unknown"
    }

    headers = {'content-type': 'application/json'}

    resp = requests.post(url, data=json.dumps(post_data), headers=headers)
    assert resp.status_code == 201

    url = "https://www.melown.com/cloud/backend/upload/file?app_id={}&access_token={}&req_scopes=MARIO_API".format(args["app_id"], args["access_token"])
    send_files(url, resp.json(), tif_file)

    resp = flask.Response(response=json.dumps({
        "file": os.path.basename(tif_file),
        "name": dataset_name
        }),
                    status=200,
                    mimetype="application/json")
    return resp
    #return 'Hello, World! {} {}'.format(outdir, outfile)

if __name__ == '__main__':
  app.run()

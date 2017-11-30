from flask import Flask
from flask import request
from flask import Response
import os
import json
import atexit
import shutil
import tempfile
import requests
import zipfile

app = Flask(__name__)
TEMPDIR = None

def clear():
    """Clear temporary files and directories
    """
    global TEMPDIR
    if TEMPDIR and os.path.isdir(TEMPDIR):
        shutil.rmtree(TEMPDIR)

atexit.register(clear)

def download_dataset(url):
    """Download zipped file from given URL, unzip

    :param url: URL of zipped archive
    :return: filename
    """

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

def upload_files(url, data, filename):
    """Upload files to created dataset. NOTE that we are using only one file
    """

    final_component = os.path.basename(filename)
    with open(filename, "rb") as tiff_data:

        files = {
            'qqfile': (
                final_component,
                open(filename, "rb").read()
            )
        }

        data = {
            'path': data["body"]["files"][0]["path"]
        }

        r = requests.post(url, files=files, data=data)
        assert r.status_code == 201

@app.route("/", methods=["POST", "GET"])
def default():
    return "Hello, world!"

@app.route("/auth", methods=["POST", "GET"])
def myauth():
    """Authorisation response - this + a bit of javascript code for oAuth
    response
    """
    # TODO: change this to template

    html_page = """
    <html>
    <head>
        <script type="text/javascript">
        var receiveMessage = function(event) {

            document.write("Message recieved");

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

@app.route('/export_mosaic', methods=["POST", "GET"])
def myexport_mosaic():
    """Export data to Melown cloud
    """

    try:
        data = request.get_json()
        args = request.args

        tif_file = download_dataset(data["download_path"])

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
        resp_json = resp.json()

        url = "https://www.melown.com/cloud/backend/upload/file?app_id={}&access_token={}&req_scopes=MARIO_API".format(args["app_id"], args["access_token"])
        upload_files(url, resp_json, tif_file)

        final_resp = Response(
            response=json.dumps({
                "file": os.path.basename(tif_file),
                "name": dataset_name,
                "dataset_id": resp_json["body"]["id"]
            }),
            status=200,
            mimetype="application/json"
        )
    finally:
        clear()
    return final_resp

if __name__ == '__main__':
  app.debug = True
  app.run()

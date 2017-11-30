# DroneDeploy server-client data export application

Exports data from DroneDeploy to Melown cloud service.

The whole repository works while deployed at http://dd-export.azurewebsites.net/ 
Microsoft Azure Python IaS infrastructure.

NOTE: This app is just proof of concept and is not intended to be used in
production environment.

## Components

There are two components: client, to be deployed as DroneDeploy javascript app
as described in https://dronedeploy.gitbooks.io/dronedeploy-apps/content/ and
server, which is deployed on Microsoft Azure.

### Client

Go to [client](client) folder and check the README.md file. It's inteded to be
used as DronDeploy client application as described https://dronedeploy.gitbooks.io/dronedeploy-apps/content/ - check the video tutorial.

### Server

Python, Flask-based simple application, which is triggerd as server hook as
described https://dronedeploy.gitbooks.io/dronedeploy-apps/content/exporter.html#orthomosaic-export
after data are ready to be exported. The server app then loads the exported
GeoTIFF to Melown Cloud automagically.

## Worflow

1. User loggs in to the DroneDeploy app.
2. User goes to desired dataset and map
3. If our app is available, automatically new Melown oAuth window is opened and
   user can log in 
4. After login, user can click the *Export* button, the rest happens behind the
   scenes
5. DroneDeploy prepares the data to export, when done, mail is send and also our
   server hook is pinged
6. Our server hook downloads the data from DroneDeploy, creates new dataset on
   Melown and uploads exported data.
7. The credentials are part of the server-hook URL 

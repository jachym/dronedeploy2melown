/**
 * DroneDeploy to Melown-cloud export app
 */

/**
 * Global vars
 */
var LOGGED_IN=false;
var OAUTH_WINDOW=null;
var CREDENTIALS = {
  access_token: null,
  state: null,
  action: null
};

var dronedeployApi = null;

var ME = {};

var IMAGES_COLLECTION = [];

/**
 * onMeSuccess
 * set ME global variable after logged in to Melown
 */
var onMeSuccess = function(response) {
  ME = response.body;
  console.log("Setting ME variable", ME)
}

/**
 * Sleep promise
 */
var sleep = function(ms){
  return new Promise(resolve => setTimeout(resolve, ms));
};

/**
 * receiveOAuthMessage 
 * Logged in to Melown-cloud
 */
var receiveOAuthMessage = function(e) {
  if (e.origin != 'http://localhost') {
    return;
  }

  if (e.origin == 'http://localhost') {
    var result = JSON.parse(e.data);
    if (result["access_token"]) {
      LOGGED_IN = true;
      OAUTH_WINDOW.close();
      CREDENTIALS.access_token = result.access_token;
      CREDENTIALS.state = result.state;
      CREDENTIALS.action = result.action;

      var meUrl = "https://www.melown.com/cloud/backend/api/me?" +
                    "access_token="+CREDENTIALS.access_token+
                    "&app_id=com.melown.jachym.drondeploy";

      jQuery.get( meUrl, null, onMeSuccess);

    }
  }
};

window.addEventListener("message", receiveOAuthMessage, false);

/**
 * Open popup for oAuth login
 */
var openOAuthPopup = function() {
  var url = "https://www.melown.com/accounts/auth/init?" +
    "service_id=mario&client_id=com.melown.jachym.drondeploy&"+
    //"redirect_uri=http://dd-export.azurewebsites.net/auth&"+
    "redirect_uri=http://localhost/drondeploy&"+
    "auth_method=standard&response_type=access_token&"+
    "scopes=MARIO_API&state=undefined";

    OAUTH_WINDOW = window.open(url);
};

/**
 * async function login_check
 * check, whether we are logged in or no - ping every 0.5s
 */
async function login_check() {
  while (LOGGED_IN === false) {
    await sleep(500);
    OAUTH_WINDOW.postMessage("Login","http://localhost");
  }
}

/**
 * new Dataset success handler
 */
var onDatasetSuccess = function(response) {
  console.log("DatasetSuccess", response);
}

/**
 * button click handler
 */
var createDataset = function() {
  var url = "https://www.melown.com/cloud/backend/api/account/" +
            ME.accounts[0].id +
            "/dataset?app_id=com.melown.jachym.drondeploy" +
            "&access_token=" + CREDENTIALS.access_token +
            "&req_scopes=MARIO_API";

  var data = {
    files: IMAGES_COLLECTION,
    name: "PokusDD-01",
    type: "unknown"
  };

  jQuery.ajax(url, {
    method: "POST",
    data: JSON.stringify(data),
    success: onDatasetSuccess,
    contentType: "application/json",
    error:function(e){console.log("DATASET ERROR", e);}
  });

};


openOAuthPopup();
login_check();

/**
 * Export 3D data
 */
var export3D = function() {

  const exportOptions = {
    // required
    layer: '3D Model',
    email: ["jachym.cepicky@gmail.com"],

    // optional
    //planId: [String], // defaults to currently visible map
    webhook: {
      url: 'http://dd-export.azurewebsites.net/' // recieve the export document when its complete
    }
  };
  dronedeployApi.Exporter.send(exportOptions)
    .then(function(exportId){ console.log(exportId) });
};

/**
 * export elevation
 */
var exportElevation = function() {
  const exportOptions = {
    // required
    layer: 'Elevation Toolbox',
    email: ["jachym.cepicky@gmail.com"],

    //optional
    file_format: "geotiff", //['geotiff', 'jpg', 'demtiff', 'contourshp', 'contourdxf'], // default to geotiff
    //merge: Boolean, // defaults to true
    //projection: Number, // defaults to 3857
    resolution: 20, // defaults to 5 (cm/px)
    //contour_interval: [Number], // default to 1 (meter)
    //planId: [String], // defaults to currently visible map
    webhook: {
      url: 'http://dd-export.azurewebsites.net/' // recieve the export document when its complete
    }
  };
  dronedeployApi.Exporter.send(exportOptions)
    .then(function(exportId){ console.log(exportId) });
};

/**
 * export mosaic
 */
var exportMosaic = function() {
  const exportOptions = {
    // required
    layer: 'Orthomosaic',
    email: ["jachym.cepicky@gmail.com"],

    //optional
    //file_format: "jpg", // default to geotiff
    //merge: Boolean, // defaults to true
    //projection: Number, // defaults to 3857
    //resolution: ['native', Number], // defaults to 5 (cm/px)
    //planId: [String], // defaults to currently visible map
    webhook: {
      url: 'http://dd-export.azurewebsites.net/export_mosaic?access_token='+
            CREDENTIALS.access_token +
            "&account_id="+ME.accounts[0].id +
            "&app_id=com.melown.jachym.drondeploy"

      // recieve the export document when its complete
    }
  };
  dronedeployApi.Exporter.send(exportOptions)
    .then(function(exportId){ console.log(exportId) });
};


new DroneDeploy({
    version: 1
  })
  .then(function(dpApi) {
      dronedeployApi = dpApi;
      return dronedeployApi.Plans.getCurrentlyViewed()
          .then(function(plan) {
              return dronedeployApi.Images.get(plan.id, {})
          })
  })
  .then(function(images) {
      /* imageOutput.innerHTML = images.map(formatOutput).join('\n');

      var data = {
          files: [],
          name: "My Name",
          type: "unknown"
      };
*/
      for (var i = 0; i < images.length; i++) {
        var image = images[i];
        //console.log(image);
        IMAGES_COLLECTION.push({
          byte_size: null,
          crs: "",
          path_component: image.data.filename
        });
      }



      /* setInterval(function(e) {
        if (auth_window.location.href.search("http://localhost") > -1) {
          clearInterval();
        }
        console.log(auth_window.location);
        console.log("#########", e);
      }, 500);
*/


      /* jQuery.post(
          "https://www.melown.com/cloud/backend/api/account/11203/dataset",
          data,
          dataset_created,
          "application/json"
        );
        */

});

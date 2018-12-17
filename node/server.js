//
// server.js
//

// express
const express = require('express');
const app = express();
const server = app.listen(3000, function(){
    console.log("Node.js is listening to PORT:" + server.address().port);
});
app.use(function(req, res, next){
    res.header("Access-Control-Allow-Origin","*");
    res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
    next();
});
app.use(express.static('public'));

// top page: telemetry
app.get('/', function(request, response) {
  response.sendFile(__dirname + '/views/index.html');
});

// latest donkey car data
let msg = {
	"throttle":	0.0,
	"angle":	0.0,
	"timestamp":	"" }

// /telem API get latest donkey car data
app.post('/telem', function(req, res) {
    if(msg) {
        // return latest donkey car data
        res.send(msg);
    } else {
        res.status(404).send();
    }
});

// MQTT Subscriber
const Client = require("ibmiotf");

// see .env
const appClientConfig  = {
  "org": process.env.ORG_ID,
  "id": process.env.APP_ID,
  "auth-key": process.env.API_KEY,
  "auth-token": process.env.SECRET_TOKEN
}

let appClient = new Client.IotfApplication(appClientConfig);

appClient.connect();

// if debug, uncomment
// trace, debug, info, warn, error
//appClient.log.setLevel('trace');

// on connect
appClient.on("connect", function () {
  //Add your code here
  console.log("on connect");
  appClient.subscribeToDeviceEvents("donkeycar","emperor");
});

// on error
appClient.on("error", function (err) {
  console.log("Error : "+err);
});

// on deviceStatus
appClient.on("deviceEvent", function (deviceType, deviceId, eventType, format, payload) {
  console.log("Device Event from :: "+deviceType+" : "+deviceId+" of event "+eventType+" with payload : "+payload);
  let message = JSON.parse(payload.toString())
  let throttle = message.throttle
  throttle = ((throttle - (-1.0))/2.0)*100.0
  message.throttle = throttle
  let angle = message.angle
  //angle = ((angle - (-1.0))/2.0)*100.0
  console.log(angle)
  message.angle = angle * 50.0
  console.log(message)
  console.log(message.timestamp)
  console.log(typeof message.angle)
  msg = message
});

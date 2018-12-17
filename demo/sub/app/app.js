// web server: express configuration
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
// telemetry ajax api
let msg = {
	"throttle":	0.0,
	"angle":	0.0,
	"timestamp":	"" }
app.post('/telemetry', function(req, res) {
    if(msg) {
        res.send(msg);
    } else {
        res.status(404).send();
    }
});
// top page
app.get('/', function(request, response) {
  response.sendFile(__dirname + '/views/index.html');
});


// mqtt client: mqtt configuration
const mqtt = require('mqtt');
// local pc
//const client = mqtt.connect('mqtt://127.0.0.1')
// docker compose
const client = mqtt.connect('mqtt://broker');
// topic name
const topic = 'test_topic/pilot'
client.subscribe(topic)
// on message callback
client.on('message', function(topic, message) {
    console.log(topic+':'+message);
    msg = message
});


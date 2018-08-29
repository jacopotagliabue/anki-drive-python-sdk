/*

ORIGINAL IDEA FROM https://github.com/adessoAG/anki-drive-java/blob/master/src/main/nodejs/server.js
CODE RE-ADAPTED AND MODIFIED FOR THE Self-driving (very small) cars BLOG SERIES
LAST UPDATE: AUG. 2018
FOR FULL LICENSE, SEE README

 */

var net = require('net');
var noble = require('noble');
var util = require('util');

// const from ANKI docs
const ANKI_DRIVE_SERVICE_UUIDS = ["be15beef6186407e83810bd89c4d8df4"];
const ANKI_DRIVE_CHARACTERISTIC_UUIDS = ["be15bee06186407e83810bd89c4d8df4", "be15bee16186407e83810bd89c4d8df4"];
// get port as the first arg from the command line
var CURRENT_PORT = parseInt(process.argv[2]);
// get current car UUID as the second arg from the command line
var CURRENT_CAR_UUID = process.argv[3];


noble.on('stateChange', function(state) {
    if (state === 'poweredOn')
    {
        console.log("powered on!");
        noble.on('discover', function(device) {
            console.log(util.format("SCAN|%s|%s", device.id, device.address));
        });
        noble.startScanning(ANKI_DRIVE_SERVICE_UUIDS);
        setTimeout(function() {
           noble.stopScanning();
           console.log("SCAN|COMPLETED");
        }, 2500);
    }
});

var server = net.createServer(function(client) {
    client.vehicles = [];

    // bind event for data received from Python app
    client.on("data", function(data) {
        data.toString().split("\r\n").forEach(function(line) {
            // parse commmand from Python
            var normalizedData = line.trim();
            var token = normalizedData.split('|');
            var command = token[0];
            var args = token.slice(1);
            console.log(util.format("command received %s", normalizedData));
            console.log(util.format("args received %s", args));
            // based on the command, execute business logic
            // default option is just gateway for bluetooth messages
            switch (command) {
                // connect to a car based on uuid, e.g. CONNECT|83d9630daa534025ab4a29a4c398d552
                case "CONNECT":
                    console.log("connection begins...");
                    var vehicle = noble._peripherals[args[0]];
                    vehicle.connect(function(error) {
                    vehicle.discoverSomeServicesAndCharacteristics(
                        ANKI_DRIVE_SERVICE_UUIDS,
	                    ANKI_DRIVE_CHARACTERISTIC_UUIDS,
                        function(error, services, characteristics) {
                          vehicle.reader = characteristics.find(x => !x.properties.includes("write"));
                          vehicle.writer = characteristics.find(x => x.properties.includes("write"));

                          vehicle.reader.notify(true);
                          vehicle.reader.on('read', function(data, isNotification) {
                              client.write(util.format("%s", data.toString("hex")));
                          });
                          client.vehicles.push(vehicle);
                          console.log("connection success!");
                        }
                    );
                  });

                    break;
                // disconnect from a car based on uuid, e.g. DISCONNECT|83d9630daa534025ab4a29a4c398d552
                case "DISCONNECT":
                    var vehicle = noble._peripherals[args[0]];
                    vehicle.disconnect();
                    console.log("disconnect success");
                    break;
                // disconnect from all cars discovered, e.g. QUIT
                case "QUIT":
                    client.vehicles.forEach(function(v) {v.disconnect()});
                    console.log("all disconnected successfully");
                    break;
                // default option: just send the message to the car unfiltered
                default:
                    console.log('run command ' + command);
                    var vehicle = noble._peripherals[CURRENT_CAR_UUID];
                    vehicle.writer.write(new Buffer(command, 'hex'));
            }
        });
    }); // on data received

    // bind event on error
    client.on("error", function(err) {
        console.log("unexpected error: disconnecting all vehicles");
        // disconnect from all vehicles
        client.vehicles.forEach(function(v) {v.disconnect()});
    }); // on error

    process.on('SIGINT', function () {
        console.log('bye bye: disconnecting all vehichles now...');
        // disconnect from all vehicles
        client.vehicles.forEach(function(v) {v.disconnect()});
        process.exit(0);
    });

});

server.listen(CURRENT_PORT);
console.log(util.format("Node gateway started, port %s, car id %s", CURRENT_PORT, CURRENT_CAR_UUID));


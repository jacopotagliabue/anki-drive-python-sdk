# py-overdrive-sdk
This is a Python wrapper to read/send message from/to [Anki Overdrive](https://www.anki.com/en-us/overdrive) 
bluetooth vehicles.

The project was designed for the A.I. blog series _Self-driving (very small) cars_:
please refer to the Medium [post](https://medium.com/@jacopotagliabue/serving-tensorflow-predictions-with-python-and-aws-lambda-facb4ab87ddd#.v01eyg8kh) 
for a full explanation on the code structure and the philosophy behind it.

## TL;DR
We share a cross-platform Python+node setup that allows for quick experimentation and prototyping of interesting ideas
in the toy universe of bluetooth cars. 
![alt text](https://lh3.googleusercontent.com/kbFYW-PYzeHWYYVNuujq33oXmul-h_dnGUJJlPQIR08lt5q7aHevYCcePW7HGWMsW6znHNv01UKukw=w2706-h1270 "Project overview")

In particular:

* a node server leverages [noble](https://www.npmjs.com/package/noble) to establish communication with 
Anki cars;
* a Python app leverages sockets to reliably read/send messages from/to the node gateway, which abstracts 
away all the complexity of the bluetooth channel.

## Setup
To use _py-overdrive-sdk_ you'll need: 

* node
* Python 3 (the project was originally coded in 3.6)
* [Anki overdrive set](https://www.anki.com/en-us/overdrive)

We run our code from a 2017 MacBook Pro and 
a [Rasp Pi 3B+](https://www.raspberrypi.org/products/raspberry-pi-3-model-b-plus/). 
We did not test with other hardware 
setups but _in theory_ the wrapper should be pretty flexible.

## Deployment
After cloning the repo, proceed to install node and python dependencies (we suggest using `virtualenv` but
it's not necessary of course) as usual:

```
npm install
```

``` 
pip install -r requirements.txt

```

Prepare the bluetooth id for the car you want to drive (if you don't know it, you can just start-up the node server with 
a fake id and write down the id that gets printed to the console in the format `SCAN|{BLUETOOTH-CAR-ID}|{BLUETOOTH-CAR-ADDRESS}`).

Start-up the node gateway:

```node node_server.js {YOUR-SERVER-PORT} {YOUR-BLUETOOTH-CAR-ID}```

and wait for the console to notify that SCAN has been completed (you should see the id of the Anki
cars as they are discovered by noble). 

Finally run your python script. To start with a simple example, run:

```python constant_speed_example.py --car={YOUR-BLUETOOTH-CAR-ID} --port={GATEWAY-PORT}```

and see your car moving around (make sure to specify the same `port` for both node and Python). [This](https://drive.google.com/file/d/1h1tjzRUQm2BZqDkZn6zhacXShGYioxgU/view) is
a one-minute video going from git to a running car: please refer to the Medium post for more details.


## Current release and next steps
Please note that the current master is released as alpha as it just contains the bare minimum 
the get things going: no unit tests, no fancy stuff, almost no protections from errors, etc. 
We'll hope to make several improvements to the code base as we progress with our experiments: 
feedback and contributions are most welcomed! Even without considering A.I. stuff (i.e. making the car 
learning how to optimally drive), there are several engineering improvements to be considered, such as for example
(non-exhaustive list in no particular order):

* set up unit and integration tests;
* re-use node gateway for multiple cars at the same time;
* a better abstraction for "driving policies", so that it becomes easier to instantiate custom policies while
keeping the rest of the code (i.e. communication layer) pretty much intact and re-usable;
* a "car-level" abstraction on top of the current Overdrive class, so that we could easily simulate different hardware 
abilities and constrain car learning in dynamic ways;
* data ingestion/persisting mechanism, so that we can log in a reliable and consistent way everything that happens
within a run


## Acknowledgments
It would have been a _month_ project, not a weekend one, without Internet and the fantastic people on it sharing their 
code and ideas: as far as copy+paste-ing goes, this project is indeed second to none. In particular:

* Python wrapper was inspired by [overdrive-python](https://github.com/xerodotc/overdrive-python)
* Node gateway was inspired by [anki-drive-java](https://github.com/adessoAG/anki-drive-java)
* Protocol and communication was reverse engineered from the official [Anki SDK](https://github.com/anki/drive-sdk) 
and [node-mqtt-for-anki-overdrive](https://github.com/IBM-Cloud/node-mqtt-for-anki-overdrive)
* Track images are from [AnkiNodeDrive](https://github.com/tiker/AnkiNodeDrive/tree/master/images)

## License
All the code in this repo is provided "AS IS" and it is freely available under the 
[Apache License Version 2.0](https://www.apache.org/licenses/LICENSE-2.0).
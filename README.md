## A.I. Duet
Trade melodies with a neural network.

## About

This experiment lets you make music through machine learning. A neural network was trained on many examples and it learns about musical concepts, building a map of notes and timings. You just play a few notes, and see how the neural net responds. We’re working on putting the experiment on the web so that anyone can play with it. In the meantime, learn about it by watching the video at this link:

[https://aiexperiments.withgoogle.com/ai-duet](https://aiexperiments.withgoogle.com/ai-duet)

This is not an official Google product.

## CREDITS

Built by [Yotam Mann](https://github.com/tambien) with friends on the Magenta and Creative Lab teams at Google. It uses [Tone.js](https://github.com/Tonejs/Tone.js) and open-source tools from the [Magenta](https://github.com/tensorflow/magenta) project. Check out more at [A.I. Experiments](https://aiexperiments.withgoogle.com).

## OVERVIEW

A.I. Duet is composed of two parts, the front-end which is in the 'static' folder and the back-end which is in the 'server' folder. The front-end client creates short midi files using the user's input which is sent to the server. The server takes that midi input and continues it using [Magenta](https://github.com/tensorflow/magenta) which is then returned back to the client. 

## DOCKER

[Docker](https://www.docker.com/) is an open-source containerization software which simplifies installation across various OSes. It is the simplest method to build and install both the front-end and back-end components. Once you have Docker installed, you can just run: 

```bash
$ sudo docker build -t ai-duet .
$ sudo docker run -t -p 8080:8080 ai-duet
```

You can now play with A.I. Duet at [localhost:8080](http://localhost:8080).

## FRONT END

If you installed with Docker, the front-end has already been built. To build the client-side javascript outside of Docker, first install [node](https://nodejs.org) and [webpack](https://webpack.github.io/). Then you can install of the dependencies of the project by typing the following in the terminal: 

```bash
cd static
npm install
```

Then build all of the files

```bash
webpack -p
```

### BACK END

If you installed with Docker, then these dependencies have already been installed. To build the back-end separately, follow these instructions: 

The back-end consists of a [Flask](http://flask.pocoo.org/) server, [TensorFlow](https://www.tensorflow.org/) and [Magenta](https://github.com/tensorflow/magenta). 

First install [TensorFlow](https://www.tensorflow.org/versions/master/get_started/os_setup.html) and [Magenta](https://github.com/tensorflow/magenta#installation).

To install the rest of the back-end requirements (make sure you have python and [pip](https://pip.pypa.io/en/stable/installing/) installed):

```bash
cd server
pip2 install -r requirements.txt
```

Then run the server:

```bash
python server.py
```

You can now play with A.I. Duet at [localhost:8080](http://localhost:8080).

## MIDI SUPPORT

The A.I. Duet supports MIDI keyboard input using [Web Midi API](https://webaudio.github.io/web-midi-api/) and the [WebMIDI](https://github.com/cotejp/webmidi) library. Make sure you refresh the page after plugging in a keyboard to make sure it connects correctly. 

## PIANO KEYBOARD

The piano can also be controlled from your computer keyboard thanks to [Audiokeys](https://github.com/kylestetz/AudioKeys). The center row of the keyboard is the white keys.

## PIANO AUDIO

Multisampled piano from [Salamander Grand Piano V3](https://archive.org/details/SalamanderGrandPianoV3) by Alexander Holm ([Creative Commons Attribution 3.0](https://creativecommons.org/licenses/by/3.0/)).

## LICENSE

Copyright 2016 Google Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

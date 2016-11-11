## [DEMO](https://tonejs.github.io/MidiConvert/)

MidiConvert makes it straightforward to work with MIDI files in Javascript. It uses [midi-file-parser](https://github.com/NHQ/midi-file-parser) to decode MIDI files and [jsmidgen](https://github.com/dingram/jsmidgen) to encode MIDI files. 


```javascript
//load a midi file
MidiConvert.load("path/to/midi.mid", function(midi){
	console.log(midi)
})
```

### Format

The data parsed from the midi file looks like this:

```javascript
{
	// the transport and timing data
	header : {
		bpm : Number,                     // the tempo, e.g. 120
		timeSignature : [Number, Number], // the time signature, e.g. [4, 4],
		PPQ : Number                  	  // the Pulses Per Quarter of the midi file
	},
	// an array of midi tracks
	tracks : [
		{
			name : String, // the track name if one was given
			notes : [
				{
					midi : Number, // midi number, e.g. 60
					time : Number, // time in seconds
					note : String, // note name, e.g. "C4"
					velocity : Number,  // normalized 0-1 velocity
					duration : String   // duration between noteOn and noteOff
				}
			],
			//midi control changes
			controlChanges : {
				//if there are control changes in the midi file
				'91' : [
					{
						number : Number // the cc number
						time : Number, // time in seconds
						value : Number  // normalized 0-1
					}
				],
			},
			instrument : String 	//the instrument if one is given
		}
	]
}
```

### Raw Midi Parsing

If you are using Node.js or have the raw binary string from the midi file, just use the `parse` method:

```javascript
fs.readFile("test.mid", "binary", function(err, midiBlob){
	if (!err){
		var midi = MidiConvert.parse(midiBlob)
	}
})
```

### Encoding Midi

You can also create midi files from scratch of by modifying an existing file. 

```javascript
//create a new midi file
var midi = MidiConvert.create()
//add a track
midi.track()
	//chain note events: note, time, duration
	.note(60, 0, 2)
	.note(63, 1, 2)
	.note(60, 2, 2)

//write the output
fs.writeFileSync("output.mid", midi.encode(), "binary")
```

### Tone.Part

The note data can be easily passed into [Tone.Part](http://tonejs.github.io/docs/#Part)

```javascript
var synth = new Tone.PolySynth(8).toMaster()

MidiConvert.load("path/to/midi.mid", function(midi){

	//make sure you set the tempo before you schedule the events
	Tone.Transport.bpm.value = midi.bpm

	//pass in the note events from one of the tracks as the second argument to Tone.Part
	var midiPart = new Tone.Part(function(time, note){

		//use the events to play the synth
		synth.triggerAttackRelease(note.name, note.duration, time, note.velocity)

	}, midi.tracks[0].notes).start()

	//start the transport to hear the events
	Tone.Transport.start()
})
```

### Acknowledgment

MidiConvert uses [midi-file-parser](https://github.com/NHQ/midi-file-parser) which is ported from [jasmid](https://github.com/gasman/jasmid) for decoding MIDI data and and [jsmidgen](https://github.com/dingram/jsmidgen) for encoding MIDI data. 
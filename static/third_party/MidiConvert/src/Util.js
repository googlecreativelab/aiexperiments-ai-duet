function cleanName(str){
	//ableton adds some weird stuff to the track
	return str.replace(/\u0000/g, '')
}

function ticksToSeconds(ticks, header){
	return (60 / header.bpm) * (ticks / header.PPQ);
}

function isNumber(val){
	return typeof val === 'number'
}

function isString(val){
	return typeof val === 'string'
}

const isPitch = (function(){
	const regexp = /^([a-g]{1}(?:b|#|x|bb)?)(-?[0-9]+)/i
	return (val) => {
		return isString(val) && regexp.test(val)
	}
}())


function midiToPitch(midi){
	const scaleIndexToNote = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];
	const octave = Math.floor(midi / 12) - 1;
	const note = midi % 12;
	return scaleIndexToNote[note] + octave;
}

const pitchToMidi = (function(){
	const regexp = /^([a-g]{1}(?:b|#|x|bb)?)(-?[0-9]+)/i
	const noteToScaleIndex = {
		"cbb" : -2, "cb" : -1, "c" : 0,  "c#" : 1,  "cx" : 2, 
		"dbb" : 0,  "db" : 1,  "d" : 2,  "d#" : 3,  "dx" : 4,
		"ebb" : 2,  "eb" : 3,  "e" : 4,  "e#" : 5,  "ex" : 6, 
		"fbb" : 3,  "fb" : 4,  "f" : 5,  "f#" : 6,  "fx" : 7,
		"gbb" : 5,  "gb" : 6,  "g" : 7,  "g#" : 8,  "gx" : 9,
		"abb" : 7,  "ab" : 8,  "a" : 9,  "a#" : 10, "ax" : 11,
		"bbb" : 9,  "bb" : 10, "b" : 11, "b#" : 12, "bx" : 13,
	}
	return (note) => {
		const split = regexp.exec(note)
		const pitch = split[1]
		const octave = split[2]
		const index = noteToScaleIndex[pitch.toLowerCase()]
		return index + (parseInt(octave) + 1) * 12
	}
}())

module.exports = {cleanName, ticksToSeconds, isString, isNumber, isPitch, midiToPitch, pitchToMidi}
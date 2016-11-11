import Tone from 'Tone/core/Tone'
import Frequency from 'Tone/type/Frequency'
import BufferSource from 'Tone/source/BufferSource'

function noteToMidi(note){
	return Frequency(note).toMidi()
}

function midiToNote(midi){
	return Frequency(midi, 'midi').toNote().replace('#', 's')
}

function midiToFrequencyRatio(midi){
	let mod = midi % 3
	if (mod === 1){
		return [midi - 1, Tone.prototype.intervalToFrequencyRatio(1)]
	} else if (mod === 2){
		return [midi + 1, Tone.prototype.intervalToFrequencyRatio(-1)]
	} else {
		return [midi, 1]
	}
}

function createSource(buffer){
	return new BufferSource(buffer)
}

export {midiToNote, noteToMidi, createSource, midiToFrequencyRatio}
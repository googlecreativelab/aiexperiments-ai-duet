import Salamander from './Salamander'
import PianoBase from './PianoBase'
import {noteToMidi, createSource, midiToFrequencyRatio} from './Util'
import Buffers from 'Tone/core/Buffers'

// the harmonics notes that Salamander has
const harmonics = [21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 51, 54, 57, 60, 63, 66, 69, 72, 75, 78, 81, 84, 87]

export default class Harmonics extends PianoBase {

	constructor(range=[21, 108]){
		super()

		const lowerIndex = harmonics.findIndex((note) => note >= range[0])
		let upperIndex = harmonics.findIndex((note) => note >= range[1])
		upperIndex = upperIndex === -1 ? upperIndex = harmonics.length : upperIndex

		const notes = harmonics.slice(lowerIndex, upperIndex)

		this._buffers = {}

		for (let n of notes){
			this._buffers[n] = Salamander.getHarmonicsUrl(n)
		}
	}

	start(note, gain, time){
		let [midi, ratio] = midiToFrequencyRatio(note)
		if (this._buffers.has(midi)){
			const source = createSource(this._buffers.get(midi)).connect(this.output)
			source.playbackRate.value = ratio
			source.start(time, 0, undefined, gain, 0)
		}
	}

	load(baseUrl){
		return new Promise((success, fail) => {
			this._buffers = new Buffers(this._buffers, success, baseUrl)
		})
	}
}
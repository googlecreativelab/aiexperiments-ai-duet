import Tone from 'Tone/core/Tone'
import Salamander from './Salamander'
import PianoBase from './PianoBase'
import {noteToMidi, createSource, midiToFrequencyRatio} from './Util'
import Buffers from 'Tone/core/Buffers'

/**
 *  Internal class
 */
class Note extends Tone{
	constructor(time, source, velocity, gain){
		super()
		//round the velocity
		this._velocity = velocity
		this._startTime = time

		this.output = source
		this.output.start(time, 0, undefined, gain, 0)
	}

	stop(time){
		if (this.output.buffer){

			// return the amplitude of the damper playback
			let progress = (time - this._startTime) / this.output.buffer.duration
			progress = (1 - progress) * this._velocity
			// stop the buffer
			this.output.stop(time, 0.2)

			return Math.pow(progress, 0.5)
		} else {
			return 0
		}
	}
}

/**
 * Maps velocity depths to Salamander velocities
 */
const velocitiesMap = {
	1  : [8],
	2  : [6, 12],
	3  : [1, 8, 15],
	4  : [1, 5, 10, 15],
	5  : [1, 4, 8, 12, 16],
	6  : [1, 3, 7, 10, 13, 16],
	7  : [1, 3, 6, 9, 11, 13, 16],
	8  : [1, 3, 5, 7, 9, 11, 13, 15],
	9  : [1, 3, 5, 7, 9, 11, 13, 15, 16],
	10 : [1, 2, 3, 5, 7, 9, 11, 13, 15, 16],
	11 : [1, 2, 3, 5, 7, 9, 11, 13, 14, 15, 16],
	12 : [1, 2, 3, 4, 5, 7, 9, 11, 13, 14, 15, 16],
	13 : [1, 2, 3, 4, 5, 7, 9, 11, 12, 13, 14, 15, 16],
	14 : [1, 2, 3, 4, 5, 6, 7, 9, 11, 12, 13, 14, 15, 16],
	15 : [1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 16],
	16 : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
}

const notes = [21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 51, 54, 57, 60, 63, 66, 69, 72, 75, 78, 81, 84, 87, 90, 93, 96, 99, 102, 105, 108]

/**
 *  Manages all of the hammered string sounds
 */
export default class Strings extends PianoBase {

	constructor(range=[21, 108], velocities=1){
		super()

		const lowerIndex = notes.findIndex((note) => note >= range[0])
		let upperIndex = notes.findIndex((note) => note >= range[1])
		upperIndex = upperIndex === -1 ? upperIndex = notes.length : upperIndex + 1

		const slicedNotes = notes.slice(lowerIndex, upperIndex)

		this._buffers = velocitiesMap[velocities].slice()

		this._buffers.forEach((vel, i) => {
			this._buffers[i] = {}
			slicedNotes.forEach((note) => {
				this._buffers[i][note] = Salamander.getNotesUrl(note, vel)
			})
		})
	}

	_hasNote(note, velocity){
		return this._buffers.hasOwnProperty(velocity) && this._buffers[velocity].has(note)
	}

	_getNote(note, velocity){
		return this._buffers[velocity].get(note)
	}

	start(note, velocity, time){

		let velPos = velocity * (this._buffers.length - 1)
		let roundedVel = Math.round(velPos)
		let diff = roundedVel - velPos
		let gain = 1 - diff * 0.5

		let [midi, ratio] = midiToFrequencyRatio(note)

		if (this._hasNote(midi, roundedVel)){
			let source = createSource(this._getNote(midi, roundedVel))
			source.playbackRate.value = ratio

			let retNote = new Note(time, source, velocity, gain).connect(this.output)

			return retNote
		} else {
			return null
		}
	}

	load(baseUrl){
		const promises = []
		this._buffers.forEach((obj, i) => {
			let prom = new Promise((success) => {
				this._buffers[i] = new Buffers(obj, success, baseUrl)
			})
			promises.push(prom)
		})
		return Promise.all(promises)
	}
}
import Util from './Util'

class Note{
	constructor(midi, time, duration=0, velocity=1){

		/**
		 * The MIDI note number
		 * @type {Number}
		 */
		this.midi;

		if (Util.isNumber(midi)){
			this.midi = midi
		} else if (Util.isPitch(midi)){
			this.name = midi
		} else {
			throw new Error('the midi value must either be in Pitch Notation (e.g. C#4) or a midi value')
		}

		/**
		 * The note on time in seconds
		 * @type {Number}
		 */
		this.time = time

		/**
		 * The duration in seconds
		 * @type {Number}
		 */
		this.duration = duration

		/**
		 * The velocity 0-1
		 * @type {Number}
		 */
		this.velocity = velocity
	}

	/**
	 * If the note is the same as the given note
	 * @param {String|Number} note
	 * @return {Boolean}
	 */
	match(note){
		if (Util.isNumber(note)){
			return this.midi === note
		} else if (Util.isPitch(note)){
			return this.name.toLowerCase() === note.toLowerCase()
		}
	}

	/**
	 * The note in Scientific Pitch Notation
	 * @type {String}
	 */
	get name(){
		return Util.midiToPitch(this.midi)
	}
	set name(name){
		this.midi = Util.pitchToMidi(name)
	}

	/**
	 * Alias for time
	 * @type {Number}
	 */
	get noteOn(){
		return this.time
	}
	set noteOn(t){
		this.time = t
	}

	/**
	 * The note off time
	 * @type {Number}
	 */
	get noteOff(){
		return this.time + this.duration
	}
	set noteOff(time){
		this.duration = time - this.time
	}

	/**
	 * Convert the note to JSON
	 * @returns {Object}
	 */
	toJSON(){
		return {
			name : this.name,
			midi : this.midi,
			time : this.time,
			velocity : this.velocity,
			duration : this.duration
		}
	}
}

export {Note}
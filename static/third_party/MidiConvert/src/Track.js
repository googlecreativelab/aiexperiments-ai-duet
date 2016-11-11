import {Note} from './Note'
import {Control} from './Control'
import {Merge} from './Merge'
import {BinaryInsert} from './BinaryInsert'

class Track {
	constructor(name='', instrument=''){

		/**
		 * The name of the track
		 * @type {String}
		 */
		this.name = name

		/**
		 * The note events
		 * @type {Array}
		 */
		this.notes = []

		/**
		 * The control changes
		 * @type {Object}
		 */
		this.controlChanges = {}

		/**
		 * The tracks insturment if one exists
		 * @type {String}
		 */
		this.instrument = ''
	}

	note(midi, time, duration=0, velocity=1){
		const note = new Note(midi, time, duration, velocity)
		BinaryInsert(this.notes, note)
		return this
	}

	/**
	 * Add a note on event
	 * @param  {Number|String} midi     The midi note as either a midi number or 
	 *                                  Pitch Notation like ('C#4')
	 * @param  {Number} time     The time in seconds
	 * @param  {Number} velocity The velocity value 0-1
	 * @return {Track} this
	 */
	noteOn(midi, time, velocity=1){
		const note = new Note(midi, time, 0, velocity)		
		BinaryInsert(this.notes, note)
		return this
	}

	/**
	 * Add a note off event. Go through and find an unresolved
	 * noteOn event with the same pitch.
	 * @param  {String|Number} midi The midi number or note name.
	 * @param  {Number} time The time of the event in seconds
	 * @return {Track} this
	 */
	noteOff(midi, time){
		for (let i = 0; i < this.notes.length; i++){
			let note = this.notes[i]
			if (note.match(midi) && note.duration === 0){
				note.noteOff = time
				break;
			}
		}
		return this
	}

	/**
	 * Add a CC event
	 * @param  {Number} num The CC number
	 * @param  {Number} time The time of the event in seconds
	 * @param {Number} value The value of the CC
	 * @return {Track} this
	 */
	cc(num, time, value){
		if (!this.controlChanges.hasOwnProperty(num)){
			this.controlChanges[num] = []
		}
		const cc = new Control(num, time, value)
		BinaryInsert(this.controlChanges[num], cc)
		return this
	}

	/**
	 * An array of all the note on events
	 * @type {Array<Object>}
	 * @readOnly
	 */
	get noteOns(){
		const noteOns = []
		this.notes.forEach((note) => {
			noteOns.push({
				time : note.noteOn,
				midi : note.midi,
				name : note.name,
				velocity : note.velocity
			})
		})
		return noteOns
	}

	/**
	 * An array of all the noteOff events
	 * @type {Array<Object>}
	 * @readOnly
	 */
	get noteOffs(){
		const noteOffs = []
		this.notes.forEach((note) => {
			noteOffs.push({
				time : note.noteOff,
				midi : note.midi,
				name : note.name
			})
		})
		return noteOffs
	}

	/**
	 * The length in seconds of the track
	 * @type {Number}
	 */
	get length() {
		return this.notes.length
	}

	/**
	 * The time of the first event in seconds
	 * @type {Number}
	 */
	get startTime() {
		if (this.notes.length){
			let firstNote = this.notes[0]
			return firstNote.noteOn
		} else {
			return 0
		}
	}

	/**
	 * The time of the last event in seconds
	 * @type {Number}
	 */
	get duration() {
		if (this.notes.length){
			let lastNote = this.notes[this.notes.length - 1]
			return lastNote.noteOff
		} else {
			return 0
		}
	}

	/**
	 * Scale the timing of all the events in the track
	 * @param {Number} amount The amount to scale all the values
	 */
	scale(amount){
		this.notes.forEach((note) => {
			note.time *= amount
			note.duration *= amount
		})
		return this
	}

	/**
	 * Slice returns a new track with only events that occured between startTime and endTime. 
	 * Modifies this track.
	 * @param {Number} startTime
	 * @param {Number} endTime
	 * @returns {Track}
	 */
	slice(startTime=0, endTime=this.duration){
		// get the index before the startTime
		const noteStartIndex = Math.max(this.notes.findIndex((note) => note.time >= startTime), 0)
		const noteEndIndex = this.notes.findIndex((note) => note.noteOff >= endTime) + 1
		const track = new Track(this.name)
		track.notes = this.notes.slice(noteStartIndex, noteEndIndex)
		//shift the start time
		track.notes.forEach((note) => note.time = note.time - startTime)
		return track
	}

	/**
	 * Write the output to the stream
	 */
	encode(trackEncoder, header){

		const ticksPerSecond = header.PPQ / (60 / header.bpm)
		let lastEventTime = 0

		const CHANNEL = 0

		function getDeltaTime(time){
			const ticks = Math.floor(ticksPerSecond * time)
			const delta = Math.max(ticks - lastEventTime, 0)
			lastEventTime = ticks
			return delta
		}

		Merge(this.noteOns, (noteOn) => {
			trackEncoder.addNoteOn(CHANNEL, noteOn.name, getDeltaTime(noteOn.time), Math.floor(noteOn.velocity * 127))
		}, this.noteOffs, (noteOff) => {
			trackEncoder.addNoteOff(CHANNEL, noteOff.name, getDeltaTime(noteOff.time))
		})
	}

}

export {Track}
import Decoder from 'midi-file-parser'
import Encoder from 'jsmidgen'
import Util from './Util'
import {Track} from './Track'
import {parseHeader} from './Header'

/**
 * @class The Midi object. Contains tracks and the header info.
 */
class Midi {
	constructor(){

		this.header = {
			//defaults
			bpm : 120,
			timeSignature : [4, 4],
			PPQ : 480
		}

		this.tracks = []
	}

	/**
	 * Load the given url and parse the midi at that url
	 * @param  {String}   url  
	 * @param {*} data Anything that should be sent in the XHR
	 * @param {String} method Either GET or POST    
	 * @return {Promise}            
	 */
	load(url, data=null, method='GET'){
		return new Promise((success, fail) => {
			var request = new XMLHttpRequest()
			request.open(method, url)
			request.responseType = 'arraybuffer'
			// decode asynchronously
			request.addEventListener('load', () => {
				if (request.readyState === 4 && request.status === 200){
					success(this.decode(request.response))
				} else {
					fail(request.status)
				}
			})
			request.addEventListener('error', fail)
			request.send(data)
		})
	}

	/**
	 * Decode the bytes
	 * @param  {String|ArrayBuffer} bytes The midi file encoded as a string or ArrayBuffer
	 * @return {Midi}       this
	 */
	decode(bytes){

		if (bytes instanceof ArrayBuffer){
			var byteArray = new Uint8Array(bytes)
			bytes = String.fromCharCode.apply(null, byteArray)
		}

		const midiData = Decoder(bytes)
		
		this.header = parseHeader(midiData)

		//replace the previous tracks
		this.tracks = []

		midiData.tracks.forEach((trackData) => {

			const track = new Track()
			this.tracks.push(track)

			let absoluteTime = 0
			trackData.forEach((event) => {
				absoluteTime += Util.ticksToSeconds(event.deltaTime, this.header)
				if (event.type === 'meta' && event.subtype === 'trackName'){
					track.name = Util.cleanName(event.text)
				} else if (event.subtype === 'noteOn'){
					track.noteOn(event.noteNumber, absoluteTime, event.velocity / 127)
				} else if (event.subtype === 'noteOff'){
					track.noteOff(event.noteNumber, absoluteTime)
				} else if (event.subtype === 'controller' && event.controllerType){
					track.cc(event.controllerType, absoluteTime, event.value / 127)
				} else if (event.type === 'meta' && event.subtype === 'instrumentName'){
					track.instrument = event.text
				}
			})
		})
		return this
	}

	/**
	 * Encode the Midi object as a Buffer String
	 * @returns {String}
	 */
	encode(){
		const output = new Encoder.File({
			ticks : this.header.PPQ
		})

		this.tracks.forEach((track, i) => {
			const trackEncoder = output.addTrack()
			trackEncoder.setTempo(this.bpm)
			track.encode(trackEncoder, this.header)
		})
		return output.toBytes()
	}

	/**
	 * Convert the output encoding into an Array
	 * @return {Array}
	 */
	toArray(){
		const encodedStr = this.encode()
		const buffer = new Array(encodedStr.length)
		for (let i = 0; i < encodedStr.length; i++){
			buffer[i] = encodedStr.charCodeAt(i)
		}
		return buffer
	}

	/**
	 * Add a new track.
	 * @param {String=} name Optionally include the name of the track
	 * @returns {Track}
	 */
	track(name){
		const track = new Track(name)
		this.tracks.push(track)
		return track
	}

	/**
	 * Get a track either by it's name or track index
	 * @param  {Number|String} trackName
	 * @return {Track}
	 */
	get(trackName){
		if (Util.isNumber(trackName)){
			return this.tracks[trackName]
		} else {
			return this.tracks.find((t) => t.name === trackName)
		}
	}

	/**
	 * Slice the midi file between the startTime and endTime. Returns a copy of the
	 * midi
	 * @param {Number} startTime
	 * @param {Number} endTime
	 * @returns {Midi} this
	 */
	slice(startTime=0, endTime=this.duration){
		const midi = new Midi()
		midi.header = this.header
		midi.tracks = this.tracks.map((t) => t.slice(startTime, endTime))
		return midi
	}

	/**
	 * the time of the first event
	 * @type {Number}
	 */
	get startTime(){
		const startTimes = this.tracks.map((t) => t.startTime)
		return Math.min.apply(Math, startTimes)
	}

	/**
	 * The bpm of the midi file in beats per minute
	 * @type {Number}
	 */
	get bpm(){
		return this.header.bpm
	}
	set bpm(bpm){
		const prevTempo = this.header.bpm
		this.header.bpm = bpm
		//adjust the timing of all the notes
		const ratio = prevTempo / bpm
		this.tracks.forEach((track) => track.scale(ratio))

	}

	/**
	 * The timeSignature of the midi file
	 * @type {Array}
	 */
	get timeSignature(){
		return this.header.timeSignature
	}
	set timeSignature(timeSig){
		this.header.timeSignature = timeSignature
	}

	/** 
	 * The duration is the end time of the longest track
	 * @type {Number}
	 */
	get duration(){
		const durations = this.tracks.map((t) => t.duration)
		return Math.max.apply(Math, durations)
	}
}

export {Midi}
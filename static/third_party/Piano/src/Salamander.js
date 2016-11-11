import {noteToMidi, midiToNote} from './Util'

export default {

	getReleasesUrl(midi){
		return `rel${midi - 20}.mp3`
	},

	getHarmonicsUrl(midi){
		return `harmL${encodeURIComponent(midiToNote(midi))}.mp3`
	},

	getNotesUrl(midi, vel){
		return `${encodeURIComponent(midiToNote(midi))}.mp3`
	}
}
import Salamander from './Salamander'
import PianoBase from './PianoBase'
import {createSource} from './Util'
import Buffers from 'Tone/core/Buffers'

export default class Release extends PianoBase {

	constructor(range){
		super()

		this._buffers = {}
		for (let i = range[0]; i <= range[1]; i++){
			this._buffers[i] = Salamander.getReleasesUrl(i)
		}
	}

	load(baseUrl){
		return new Promise((success) => {
			this._buffers = new Buffers(this._buffers, success, baseUrl)
		})
	}
	
	start(note, time){
		if (this._buffers.has(note)){
			let source = createSource(this._buffers.get(note)).connect(this.output)
			source.start(time, 0, undefined, 0.01, 0)
		}
	}
}
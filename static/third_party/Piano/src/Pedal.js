import PianoBase from './PianoBase'
import Salamander from './Salamander'
import {createSource} from './Util'
import Buffers from 'Tone/core/Buffers'

export default class Pedal extends PianoBase {
	constructor(load=true){
		super()

		this._downTime = Infinity

		this._currentSound = null

		this._buffers = null

		this._loadPedalSounds = load
	}

	load(baseUrl){
		if (this._loadPedalSounds){
			return new Promise((success) => {			
				this._buffers = new Buffers({
					up : 'pedalU1.mp3',
					down : 'pedalD1.mp3'
				}, success, baseUrl)
			})
		} else {
			return Promise.resolve()			
		}
	}

	/**
	 *  Squash the current playing sound
	 */
	_squash(time){
		if (this._currentSound){
			this._currentSound.stop(time, 0.1)
		}
		this._currentSound = null
	}

	_playSample(time, dir){
		if (this._loadPedalSounds){
			this._currentSound = createSource(this._buffers.get(dir))
			this._currentSound.connect(this.output).start(time, 0, undefined, 0.2)
		}
	}

	down(time){
		this._squash(time)
		this._downTime = time
		this._playSample(time, 'down')
	}

	up(time){
		this._squash(time)
		this._downTime = Infinity
		this._playSample(time, 'up')
	}

	isDown(time){
		return time > this._downTime
	}
}
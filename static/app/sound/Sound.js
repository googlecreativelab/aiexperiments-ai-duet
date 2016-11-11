/**
 * Copyright 2016 Google Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import Piano from 'Piano/src/Piano'
import Tone from 'Tone/core/Tone'
import PolySynth from 'Tone/instrument/PolySynth'
import Frequency from 'Tone/type/Frequency'
import MonoSynth from 'Tone/instrument/MonoSynth'

class Sound {
	constructor(){

		this._range = [36, 108]

		/**
		 * The piano audio
		 * @type {Piano}
		 */
		this._piano = new Piano(this._range, 1, false).toMaster().setVolume('release', -Infinity)

		/**
		 * The piano audio
		 * @type {Piano}
		 */
		this._aipiano = new Piano(this._range, 1, false).toMaster().setVolume('release', -Infinity)

		this._synth = new PolySynth(8, MonoSynth).toMaster()
		this._synth.set({
			oscillator : {
				type : 'pwm',
				modulationFrequency : 3
			},
			envelope : {
				attackCurve : 'linear',
				attack : 0.05,
				decay : 0.3,
				sustain : 0.8,
				release : 3,
			},
			filter : {
				type : 'lowpass'
			},
			filterEnvelope : {
				baseFrequency : 800,
				octaves : 1,
				attack : 0.3,
				decay : 0.1,
				sustain : 1,
				release : 3,	
			}
		})
		this._synth.volume.value = -36

		window.synth = this._synth
	}

	load(){
		const salamanderPath = 'audio/Salamander/'

		return Promise.all([this._piano.load(salamanderPath), this._aipiano.load(salamanderPath)])
	}

	keyDown(note, time=Tone.now(), ai=false){

		if (note >= this._range[0] && note <= this._range[1]){
			if (ai){
				this._aipiano.keyDown(note, 1, time)
				this._synth.triggerAttack(Frequency(note, 'midi').toNote(), time)
			} else {
				this._piano.keyDown(note, 1, time)
			}
		}

	}

	keyUp(note, time=Tone.now(), ai=false){
		if (note >= this._range[0] && note <= this._range[1]){
			if (ai){
				this._aipiano.keyUp(note, time)
				this._synth.triggerRelease(Frequency(note, 'midi').toNote(), time)
			} else {
				this._piano.keyUp(note, time)
			}
		}
	}
}

export {Sound}
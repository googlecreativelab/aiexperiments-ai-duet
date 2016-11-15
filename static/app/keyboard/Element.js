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

import events from 'events'
import 'style/keyboard.css'
import 'pepjs'
import {Roll} from 'roll/Roll'


const offsets = [0, 0.5, 1, 1.5, 2, 3, 3.5, 4, 4.5, 5, 5.5, 6]

class KeyboardElement extends events.EventEmitter {

	constructor(container, lowest=36, octaves=4){
		super()
		this._container = document.createElement('div')
		this._container.id = 'keyboard'
		container.setAttribute('touch-action', 'none')
		container.addEventListener('pointerup', () => this._mousedown = false)
		container.appendChild(this._container)

		this._keys = {}

		this._mousedown = false

		this.resize(lowest, octaves)

		/**
		 * The piano roll
		 * @type {Roll}
		 */
		this._roll = new Roll(container)
	}

	resize(lowest, octaves){
		this._keys = {}
		// clear the previous ones
		this._container.innerHTML = ''
		// each of the keys
		const keyWidth = (1 / 7) / octaves
		for (let i = lowest; i < lowest + octaves * 12; i++){
			let key = document.createElement('div')
			key.classList.add('key')
			let isSharp = ([1, 3, 6, 8, 10].indexOf(i % 12) !== -1)
			key.classList.add(isSharp ? 'black' : 'white')
			this._container.appendChild(key)
			// position the element
			
			let noteOctave = Math.floor(i / 12) - Math.floor(lowest / 12)
			let offset = offsets[i % 12] + noteOctave * 7
			key.style.width = `${keyWidth * 100}%`
			key.style.left = `${offset * keyWidth * 100}%`
			key.id = i.toString()
			key.setAttribute('touch-action', 'none')

			const fill = document.createElement('div')
			fill.id = 'fill'
			key.appendChild(fill)
			
			this._bindKeyEvents(key)
			this._keys[i] = key

		}
	}

	_bindKeyEvents(key){

		key.addEventListener('pointerover', (e) => {
			if (this._mousedown){
				const noteNum = parseInt(e.target.id)
				// this.keyDown(noteNum, false)
				this.emit('keyDown', noteNum)
			} else {
				key.classList.add('hover')
			}
		})
		key.addEventListener('pointerout', (e) => {
			if (this._mousedown){
				const noteNum = parseInt(e.target.id)
				// this.keyUp(noteNum, false)
				this.emit('keyUp', noteNum)
			} else {
				key.classList.remove('hover')
			}
		})
		key.addEventListener('pointerdown', (e) => {
			e.preventDefault()
			const noteNum = parseInt(e.target.id)
			// this.keyDown(noteNum, false)
			this.emit('keyDown', noteNum)
			this._mousedown = true
		})
		key.addEventListener('pointerup', (e) => {
			e.preventDefault()
			const noteNum = parseInt(e.target.id)
			// this.keyUp(noteNum, false)
			this.emit('keyUp', noteNum)
			this._mousedown = false
		})
	}

	keyDown(noteNum, ai=false){
		// console.log('down', noteNum, ai)
		if (this._keys.hasOwnProperty(noteNum)){
			const key = this._keys[noteNum]
			key.classList.remove('hover')

			const highlight = document.createElement('div')
			highlight.classList.add('highlight')
			highlight.classList.add('active')
			if (ai){
				highlight.classList.add('ai')
			}
			key.querySelector('#fill').appendChild(highlight)

			this._roll.keyDown(noteNum, this._getNotePosition(noteNum), ai)
		}
	}

	keyUp(noteNum, ai=false){
		// console.log('up', noteNum, ai)
		if (this._keys.hasOwnProperty(noteNum)){
			const query = ai ? '.highlight.active.ai' : '.highlight.active'
			const highlight = this._keys[noteNum].querySelector(query)
			if (highlight){
				highlight.classList.remove('active')
				setTimeout(() => highlight.remove(), 2000)
				//and up on the roll
			} else {
				//try again
				this.keyUp(noteNum)
			}
		}	
		this._roll.keyUp(noteNum, ai)
	}

	_getNotePosition(key){
		if (this._keys.hasOwnProperty(key)){
			return this._keys[key].querySelector('#fill').getBoundingClientRect()
		}		
	}
}

export {KeyboardElement}
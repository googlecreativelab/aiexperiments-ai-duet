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

import {Keyboard} from 'keyboard/Keyboard'
import domReady from 'domready'
import 'style/main.css'
import {AI} from 'ai/AI'
import {Sound} from 'sound/Sound'
import {Glow} from 'interface/Glow'
import {Splash} from 'interface/Splash'

domReady(() => {

	const container = document.createElement('div')
	container.id = 'container'
	document.body.appendChild(container)

	const ai = new AI()
	const glow = new Glow(container)
	const keyboard = new Keyboard(container)
	const sound = new Sound()

	const splash = new Splash(document.body)
	splash.on('click', () => {
		container.classList.add('focus')
		keyboard.activate()
	})

	sound.load()

	keyboard.on('keyDown', (note) => {
		sound.keyDown(note)
		ai.keyDown(note)
		glow.user()
	})

	keyboard.on('keyUp', (note) => {
		sound.keyUp(note)
		ai.keyUp(note)
		glow.user()
	})

	ai.on('keyDown', (note, time) => {
		sound.keyDown(note, time, true)
		keyboard.keyDown(note, time, true)
		glow.ai(time)
	})

	ai.on('keyUp', (note, time) => {
		sound.keyUp(note, time, true)
		keyboard.keyUp(note, time, true)	
		glow.ai(time)
	})

})
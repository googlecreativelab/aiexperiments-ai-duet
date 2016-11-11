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

import Buffer from 'Tone/core/Buffer'
import 'style/splash.css'
import events from 'events'
import Loader from 'interface/Loader'

class Splash extends events.EventEmitter{
	constructor(container){

		super()
		const splash = document.createElement('div')
		splash.id = 'splash'
		container.appendChild(splash)

		// the title
		const titleContainer = document.createElement('div')
		titleContainer.id = 'titleContainer'
		splash.appendChild(titleContainer)

		const title = document.createElement('div')
		title.id = 'title'
		title.textContent = 'A.I. Duet'
		titleContainer.appendChild(title)

		const subTitle = document.createElement('div')
		subTitle.id = 'subTitle'
		titleContainer.appendChild(subTitle)
		subTitle.textContent = 'Trade melodies with a neural network.'

		const loader = new Loader(titleContainer)
		loader.on('click', () => {
			splash.classList.add('disappear')
			this.emit('click')
		})

		const aiExperiments = document.createElement('a')
		aiExperiments.id = 'aiExperiments'
		aiExperiments.href = 'https://aiexperiments.withgoogle.com'
		aiExperiments.target = '_blank'
		splash.appendChild(aiExperiments)

		// break
		const badgeBreak = document.createElement('div')
		badgeBreak.id = 'badgeBreak'
		splash.appendChild(badgeBreak)		

		const googleFriends = document.createElement('a')
		googleFriends.id = 'googleFriends'
		splash.appendChild(googleFriends)

		const privacyAndTerms = document.createElement('div')
		privacyAndTerms.id = 'privacyAndTerms'
		privacyAndTerms.innerHTML = '<a target="_blank" href="https://www.google.com/intl/en/policies/privacy/">Privacy</a><span>&</span><a target="_blank" href="https://www.google.com/intl/en/policies/terms/">Terms</a>'
		splash.appendChild(privacyAndTerms)

	}
}

export {Splash}
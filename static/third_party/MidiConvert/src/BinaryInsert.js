/**
 * Return the index of the element at or before the given time
 */
function findElement(array, time) {
	let beginning = 0
	const len = array.length
	let end = len
	if (len > 0 && array[len - 1].time <= time){
		return len - 1
	}
	while (beginning < end){
		// calculate the midpoint for roughly equal partition
		let midPoint = Math.floor(beginning + (end - beginning) / 2)
		const event = array[midPoint]
		const nextEvent = array[midPoint + 1]
		if (event.time === time){
			//choose the last one that has the same time
			for (let i = midPoint; i < array.length; i++){
				let testEvent = array[i]
				if (testEvent.time === time){
					midPoint = i
				}
			}
			return midPoint
		} else if (event.time < time && nextEvent.time > time){
			return midPoint
		} else if (event.time > time){
			//search lower
			end = midPoint
		} else if (event.time < time){
			//search upper
			beginning = midPoint + 1
		} 
	}
	return -1
}

/**
 * Does a binary search to insert the note
 * in the correct spot in the array
 * @param  {Array} array
 * @param  {Object} event
 * @param  {Number=} offset
 */
function BinaryInsert(array, event){
	if (array.length){
		const index = findElement(array, event.time)
		array.splice(index + 1, 0, event)
	} else {
		array.push(event)
	}
}

export {BinaryInsert}
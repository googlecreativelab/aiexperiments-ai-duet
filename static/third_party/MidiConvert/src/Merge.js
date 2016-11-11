
function hasMoreValues(arrays, positions){
	for (let i = 0; i < arrays.length; i++){
		let arr = arrays[i]
		let pos = positions[i]
		if (arr.length > pos){
			return true
		}
	}
	return false
}

function getLowestAtPosition(arrays, positions, encoders){
	let lowestIndex = 0
	let lowestValue = Infinity
	for (let i = 0; i < arrays.length; i++){
		let arr = arrays[i]
		let pos = positions[i]
		if (arr[pos] && (arr[pos].time < lowestValue)){
			lowestIndex = i
			lowestValue = arr[pos].time
		}
	}
	encoders[lowestIndex](arrays[lowestIndex][positions[lowestIndex]])
	// increment array
	positions[lowestIndex] += 1
}

/**
 * Combine multiple arrays keeping the timing in order
 * The arguments should alternate between the array and the encoder callback
 * @param {...Array|Function} args
 */
function Merge(...args){
	const arrays = args.filter((v, i) => (i % 2) === 0)
	const positions = new Uint32Array(arrays.length)
	const encoders = args.filter((v, i) => (i % 2) === 1)
	const output = []
	while(hasMoreValues(arrays, positions)){
		getLowestAtPosition(arrays, positions, encoders)
	}
}

export {Merge}
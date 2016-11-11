import {Midi} from './Midi'

const MidiConvert = {
	/**
	 *  Parse all the data from the Midi file into this format:
	 *  {
	 *  	// the transport and timing data
	 *  	header : {
	 *  		bpm : Number,                     // tempo, e.g. 120
	 *  		timeSignature : [Number, Number], // time signature, e.g. [4, 4],
	 *  		PPQ : Number                  // PPQ of the midi file
	 *  	},
	 *  	// an array for each of the midi tracks
	 *  	tracks : [
	 *  		{
	 *  			name : String, // the track name if one was given
	 *  			notes : [
	 *  				{
	 *  					time : Number, // time in seconds
	 *  					name : String, // note name, e.g. 'C4'
	 *  					midi : Number, // midi number, e.g. 60
	 *  					velocity : Number,  // normalized velocity
	 *  					duration : Number   // duration between noteOn and noteOff
	 *  				}
	 *  			],
	 *  			controlChanges : { //all of the control changes
	 *  				64 : [ //array for each cc value
	 *  					{
	 *  						number : Number, //the cc number
	 *  						time : Number, //the time of the event in seconds
	 *  						name : String, // if the cc value has a common name (e.g. 'sustain')
	 *  						value : Number, //the normalized value
	 *  					}
	 *  				]
	 *  			}
	 *  		}
	 *  	]
	 *  }
	 *  @param  {Binary String}  fileBlob  The output from fs.readFile or FileReader
	 *  @returns {Object} All of the options parsed from the midi file. 
	 */
	parse : function(fileBlob){
		return new Midi().decode(fileBlob)
	},
	/**
	 *  Load and parse a midi file. See `parse` for what the results look like.
	 *  @param  {String}    url
	 *  @param {Function=} callback
	 *  @returns {Promise} A promise which is invoked with the returned Midi object
	 */
	load : function(url, callback){
		const promise = new Midi().load(url)
		if (callback){
			promise.then(callback)
		}
		return promise
	},
	/**
	 * Create an empty midi file
	 * @return {Midi}
	 */
	create : function(){
		return new Midi()
	}
}

export default MidiConvert

module.exports = MidiConvert

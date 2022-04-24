const { Control } = require('magic-home');

const ip = "10.10.123.3"
const wait_for_reply = false

const control = new Control(ip, { wait_for_reply });

var last_change = 0;
var last_color = 0;

control.startEffectMode().then(effects => {
	effects.start(interval_function);
}).catch(err => {
	console.log("Error while connecting:", err.message);
});

function interval_function() {
	let now = (new Date()).getTime();

	if (now - last_change < 1000) {
		return this.delay(Math.max(0, 1000 - (now - last_change)));
	} else {
		last_color = (last_color + 1) % 3;
		last_change = now;

		switch(last_color) {
			case 0:
				return this.setColor(255, 0, 0);
			case 1:
				return this.setColor(0, 255, 0);
			case 2:
				return this.setColor(0, 0, 255);
		}		
	}
}
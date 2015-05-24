var orientation = null;
var motors = null;
var model = null;
var terminal = null;
$(document).ready(function () {
    $('#compass').load(function () {
        orientation = document.getElementById('compass').contentWindow;
    });
    $('#motors').load(function () {
        motors = document.getElementById('motors').contentWindow;
    });
    $('#model').load(function () {
        model = document.getElementById('model').contentWindow;
    });
    $('#terminal').load(function () {
        terminal = document.getElementById('terminal').contentWindow;
    });

    setInterval(function () {
        update();
    }, 240);
});

function update() {
    $.get('api/get_gui()', function( data ) {
        if(orientation==0) {
            orientation = document.getElementById('compass').contentDocument.window;
        }
        if(motors==0) {
            motors = document.getElementById('motors').contentDocument.window;
        }
        if(model==0) {
            model = document.getElementById('model').contentDocument.window;
        }
        if(terminal==0) {
            terminal = document.getElementById('terminal').contentDocument.window;
        }

        data = JSON.parse(data);
        var motor_speeds = data['motors'];
        var positions = data['position'];
        var log = data['log'];
        for(var motor in motor_speeds) {
            motors.setProgress(motor, Math.abs(motor_speeds[motor]));
        }

        orientation.setRoll(positions['roll']);
        orientation.setPitch(positions['pitch']);
        orientation.setHeading(positions['yaw']);
        model.setRoll(positions['roll']);
        model.setPitch(positions['pitch']);
        for(var i in log) {
            terminal.log(log[i][0], log[i][1], log[i][2]);
        }
    });
}
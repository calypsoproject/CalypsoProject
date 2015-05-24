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

    setInterval(function () {
        update();
    }, 240);
});

function update() {
    $.get('api/get_gui()', function( data ) {
        data = JSON.parse(data);
        var motor_speeds = data['motors'];
        var positions = data['position'];
        for(var motor in motor_speeds) {
            motors.setProgress(motor, Math.abs(motor_speeds[motor]));
        }

        orientation.setRoll(positions['roll']);
        orientation.setPitch(positions['pitch']);
        orientation.setHeading(positions['yaw']);
        model.setRoll(positions['roll']);
        model.setPitch(positions['pitch']);
    });
}
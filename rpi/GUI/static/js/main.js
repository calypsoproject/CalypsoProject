var orientation = null;
var motors = null;
var model = null;
var terminal = null;
$(document).ready(function () {
    $.get('api/motor_handler.motor["fr"].get_motor_state()', function (data) {
        if (data == 1) {
            system_state = true;
            enable_system_btn.css('background-color', '#93332C');
            enable_system_btn.text('disable system');
        }
    });
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
    }, 250);
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

var system_state = false;
var enabling = false;
function systemBtnClick() {
    $.get('api/motor_handler.motor["fr"].get_motor_state()', function (data) {
        if(data == 1) {
            system_state=true;
        }
    });
    var enable_system_btn = $('#enable-system');
    if(!system_state && !enabling) {
        $.get('api/motor_handler.enable()', function( data ) {});
        enable_system_btn.css('background-color', '#CA6B11');
        enable_system_btn.text('enabling...');
        enabling = true;
        setTimeout(function () {
            enabling = false;
            system_state = true;
            enable_system_btn.css('background-color', '#93332C');
            enable_system_btn.text('disable system');
        }, 8000)
    } else if(!enabling) {
        $.get('api/motor_handler.disable()', function( data ) {});
        enable_system_btn.css('background-color', '#429042');
        enable_system_btn.text('enable system');
        enabling = false;
        system_state = false;
    }
}
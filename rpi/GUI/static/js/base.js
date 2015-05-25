$(document).ready(function() {
    $.get( "api/pid_roll.Kp", function( data ) {
		$( "#Kpr" ).val(data);
	});
    $.get( "api/pid_roll.Ki", function( data ) {
		$( "#Kir" ).val(data);
	});
    $.get( "api/pid_roll.Kd", function( data ) {
		$( "#Kdr" ).val(data);
	});

    $.get( "api/pid_pitch.Kp", function( data ) {
		$( "#Kpp" ).val(data);
	});
    $.get( "api/pid_pitch.Ki", function( data ) {
		$( "#Kip" ).val(data);
	});
    $.get( "api/pid_pitch.Kd", function( data ) {
		$( "#Kdp" ).val(data);
	});

    $.get( "api/pid_pitch.Kp", function( data ) {
		$( "#Kp" ).val(data);
	});
    $.get( "api/pid_pitch.Ki", function( data ) {
		$( "#Ki" ).val(data);
	});
    $.get( "api/pid_pitch.Kd", function( data ) {
		$( "#Kd" ).val(data);
	});



	$.get( "api/speed_calculator.floating_speed", function( data ) {
		$('#fs').val(data);
	});

	$.get( "api/speed_calculator.max_speed", function( data ) {
		$('#maxs').val(data);
	});

	$.get( "api/speed_calculator.min_speed", function( data ) {
		$('#mins').val(data);
	});

	$.get( "api/speed_calculator.max_roll", function( data ) {
		$('#ra').val(data);
	});

	$.get( "api/speed_calculator.max_incline", function( data ) {
		$('#pa').val(data);
	});
});

function api(action) {
    $.get( "api/"+action, function( data ) {
		$( "#last_response" ).text(data);
	});
}

function change_speed(speed, motor) {
	$.get( "api/"+motor+".set_speed("+speed+")", function( data ) {
		$( "#last_response" ).text(data);
	});
}

function set_accel(accel) {
	$.get( "api/motor_handler.set_accel("+accel+")", function( data ) {
		$( "#last_response" ).text(data);
	});	
}

function disable_system() {
	for(var i=1; i<7; i++) {
		$('#motor_text_'+i).val(0);
		$('#motor'+i).val(0);
		$('#state').text('0');
	}
}

function updatePid(Kp, Ki, Kd){
    $.get( "api/pid_roll.update("+Kp+", "+Ki+", "+Kd+")", function( data ) {
		$('#last_response').text(data);
    });
	$.get( "api/pid_pitch.update("+Kp+", "+Ki+", "+Kd+")", function( data ) {
		$('#last_response').text(data);
    });
}

function updatePidRoll(Kp, Ki, Kd){
    $.get( "api/pid_roll.update("+Kp+", "+Ki+", "+Kd+")", function( data ) {
		$('#last_response').text(data);
    });
}

function updatePidPitch(Kp, Ki, Kd){
	$.get( "api/pid_pitch.update("+Kp+", "+Ki+", "+Kd+")", function( data ) {
		$('#last_response').text(data);
    });
}
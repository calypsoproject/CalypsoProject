$(document).ready(function() {
    $.get( "api/pid.Kp("+speed+")", function( data ) {
		$( "#Kp" ).text(data);
	});
    $.get( "api/pid.Ki("+speed+")", function( data ) {
		$( "#Ki" ).text(data);
	});
    $.get( "api/pid.Kd("+speed+")", function( data ) {
		$( "#Kd" ).text(data);
	});

});

function api(action) {
    $.get( "api/"+action+"\"", function( data ) {
		$( "#last_response" ).text(data);
	});
}

function change_speed(speed, motor) {
	$.get( "api/"+motor+".set_speed("+speed+")", function( data ) {
		$( "#last_response" ).text(data);
	});
}

function set_kp(kp) {
	$.get( "api/motor_handler.set_kp("+kp+")", function( data ) {
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
    $.get( "api/pid.update("+Kp+", "+Ki+", "+Kd+")", function( data ) {

    });
}
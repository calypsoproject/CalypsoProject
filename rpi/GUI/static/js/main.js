$(document).ready(function() {
});

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
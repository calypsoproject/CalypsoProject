$( document ).ready(function() {
	change_progress_bar('.pbars', '60%');
});

function visually_disable_motor(id) {
	$(id).css({'border-color': '#AFAFAF'});
	change_progress_bar(id, '0%');
}

function visually_enable_motor(id) {
	$(id).css({'border-color': '#3ADD36'});
}

function rikvrc(id) {
	$(id + ' > div').css({'background-color': '#F08F00'});
	$(id).css({'border-color': '#F08F00'});
}

function naprej(id) {
	$(id + ' > div').css({'background-color': '#3ADD36'});	
	$(id).css({'border-color': '#3ADD36'});
}

function change_progress_bar(id, height) {
	$(id + ' > div').clearQueue().animate({'height': height}, 600);
	update_text(id, height, 0);
}

function update_text(id, height, i) {
	$(id + ' > div > t').text(Math.round($(id + ' > div').height() / $(id + ' > div').parent().height() * 100) + '%');	
	i++;
	if(i < 50) {
		setTimeout(function() {update_text(id, height, i);}, 10);
	} else {
		$(id + ' > div > t').text(height);
	}
}
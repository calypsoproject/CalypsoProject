$( document ).ready(function() {
	change_progress_bar('.pbars', '70%');
});

function change_progress_bar(id, height) {
	$(id + ' > div').animate({'height': height}, 500);
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
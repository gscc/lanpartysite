$(document).ready(function() {
	$('.show-trailer-button').click(function() {
		$('.trailer').toggle(400);
		if ($(this).html() == 'Show Trailer') {
			$(this).html('Hide Trailer');
		} else {
			$(this).html('Show Trailer');
		}
	});
});
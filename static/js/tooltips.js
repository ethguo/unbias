$(document).ready(function()
{
	$('.tooltip-text').each(function() {
		$(this).qtip({
			content: {
				text: $(this).next('.tooltip-content')
			},
			hide: {
				fixed: true,
				delay: 300
			},
			style: {
				classes: "qtip-bootstrap"
			},
			position: {
				my: "top left",
				at: "bottom left"
			}
		});
	});
});
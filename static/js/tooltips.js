// Create the tooltips only when document ready
$(document).ready(function()
{
	// MAKE SURE YOUR SELECTOR MATCHES SOMETHING IN YOUR HTML!!!
	$('.tooltip-text').each(function() {
		$(this).qtip({
			content: {
				text: $(this).next('.tooltip-content')
			},
			hide: {
				fixed: true,
				delay: 300
			}
		});
	});
});
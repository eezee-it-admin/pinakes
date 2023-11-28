$(document).ready(function() {

    $(document).on('click', 'a.smooth-scroll-link', function(event) {
        event.preventDefault();

        var target = $($.attr(this, 'href'));
        if (target.length) {
            $('html, body').animate({
                scrollTop: target.offset().top
            }, 500);
        }
    });
});

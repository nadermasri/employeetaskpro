$(document).ready(function() {
    const updateActiveNav = () => {
        const path = window.location.pathname;
        $('#navbarSupportedContent .nav-link').each(function() {
            if ($(this).attr('href') === path) {
                $(this).closest('.nav-item').addClass('active');
            }
        });
    };

    // Update active nav item on page load
    updateActiveNav();

    // Responsive Navbar Toggle
    $('.navbar-toggler').click(function() {
        $('.navbar-collapse').slideToggle();
    });

    // Update Navbar on window resize
    $(window).resize(function() {
        clearTimeout(window.resizedFinished);
        window.resizedFinished = setTimeout(function(){
            updateActiveNav();
        }, 250);
    });

    // Add active class on navbar item click
    $('#navbarSupportedContent .nav-item').on('click', function() {
        $('#navbarSupportedContent .nav-item').removeClass('active');
        $(this).addClass('active');
    });
});

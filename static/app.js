// collapse nav bar when clicked on mobile
$('.navbar-nav>li>a')
    .on('click', function() {
        $('.navbar-collapse')
            .collapse('hide');
    });
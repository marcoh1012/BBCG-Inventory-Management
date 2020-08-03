$('#jobs')
    .on('click', viewJobs)

$('#slabs')
    .on('click', viewSlabs)
$('#jobs-mobile')
    .on('click', viewJobs)

$('#slabs-mobile')
    .on('click', viewSlabs)

// collapse nav bar when clicked on mobile
$('.navbar-nav>li>a')
    .on('click', function() {
        $('.navbar-collapse')
            .collapse('hide');
    });

function viewJobs(evt) {
    evt.preventDefault()
    $('.slabs-info')
        .hide();
    $('.jobs-info')
        .show();
}

function viewSlabs(evt) {
    evt.preventDefault()
    $('.slabs-info')
        .show();
    $('.jobs-info')
        .hide();
}
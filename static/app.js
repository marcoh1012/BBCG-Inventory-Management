$('#jobs')
    .on('click', viewJobs)

$('#slabs')
    .on('click', viewSlabs)

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
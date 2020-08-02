$('#jobs')
    .on('click', viewJobs)

$('#slabs')
    .on('click', viewSlabs)

function viewJobs(evt) {
    $('.slabs-info')
        .hide();
    $('.jobs-info')
        .show();
}

function viewSlabs(evt) {
    $('.slabs-info')
        .show();
    $('.jobs-info')
        .hide();
}
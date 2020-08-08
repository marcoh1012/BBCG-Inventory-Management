// collapse nav bar when clicked on mobile
$('.navbar-nav>li>a')
    .on('click', function() {
        $('.navbar-collapse')
            .collapse('hide');
    });
// print barcode
function printBarcode(url) {
    let win = window.open('');
    win.document.write(`<img src="${url}"  onload="window.print();window.close()" >`);
    win.focus();
}




function addSlabSF(slabID, jobID) {
    $('#addslabsf')
        .modal('show');
    let $form = $('#form4')[0]
    $form.action = `/job/${jobID}/${slabID}/addslabsf`;
}
cutout = 0;
slab = 0;
edge_id = 0;
job_cutout_id = 0;

let $delete_item;

function deleteCutout(job_id, id) {
    cutout = id;
    job_cutout_id = job_id;
    $('#delete_modal')
        .modal('show');
    $delete_item = $('.delete-btn')[0]
    $delete_item.setAttribute('href', `/job/${job_cutout_id}/cutout/${cutout}/delete`)
}

function deleteSlab(job_id, slab_id) {
    slab = slab_id;
    job_cutout_id = job_id;
    $('#delete_modal')
        .modal('show');
    $delete_item = $('.delete-btn')[0]
    $delete_item.setAttribute('href', `/job/${job_cutout_id}/slab/${slab}/delete`)

}

function deleteEdge(job_id, edge_id) {
    edge = edge_id;
    job_cutout_id = job_id;
    $('#delete_modal')
        .modal('show');
    $delete_item = $('.delete-btn')[0]
    $delete_item.setAttribute('href', `/job/${job_cutout_id}/edge/${edge}/delete`)
}
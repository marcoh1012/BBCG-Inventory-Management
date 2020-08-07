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

let slab_id = 0;


function addSlabSF(slabID, jobID) {
    $('#addslabsf').modal('show');
    let $form = $('#form4')[0]
    $form.action = `/job/${jobID}/${slabID}/addslabsf`;
}

// $('.add-sf-btn').on('click', (evt) => {
//     alert('also')
//     evt.preventDefault();
//     $('.add-sf-btn').action = `/slab/${slab_id}`
//     $('.add-sf-btn').submit()
// })

// function submit_add_sf_form() {
//     alert('submitted')
//     console.log($form)
//     $form.target = '_blank';
//     $form.action = `/slab/${slab_id}`;
//     //$form.submit();
// }
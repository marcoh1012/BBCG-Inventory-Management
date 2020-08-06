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
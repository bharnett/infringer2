
function showStatus(isError, message) {
    PNotify.prototype.options.styling = 'fontawesome';
    new PNotify({
        title: isError ? 'Error' : 'Success',
        text: message,
        icon: true,
        type: isError ? 'error' : 'success'
    });
}
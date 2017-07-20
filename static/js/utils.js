
function showStatus(isError, message) {
    PNotify.prototype.options.styling = 'fontawesome';
    new PNotify({
        title: isError ? 'Error' : 'Success',
        text: message,
        icon: true,
        type: isError ? 'error' : 'success'
    });
}

function getParameterByName(name, url) {
    if (!url) url = window.location.href;
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}

function updateText(elem, text, isPrepend = false){
    var cache = $(elem).children();
    if (isPrepend)
    {
        $(elem).text(text).prepend(cache);
    }
    else {
        $(elem).text(text).append(cache);
    }
}
function AddValidationExts() {

    $.validator.addMethod('domainChecker', function (value) {
        var isValid = true;
        allUrls = value.split(',');
        for (i = 0; i < allUrls.length; i++) {
            isValid = /^[A-Za-z0-9-]{1,63}\.+[A-Za-z]{2,6}$/.test(allUrls[i].trim());
            if (isValid == false) {
                break;
            }
        }
        return isValid

        //return /^[A-Za-z0-9-]{1,63}\.+[A-Za-z]{2,6}$/.test(value);
    }, 'Invalid domain(s) (ex: mydomain.com)');

    $.validator.addMethod('IP4Checker', function (value) {
        var pieces = value.split('.');
        if (pieces.length != 4) {
            return false;
        } else {
            var isValid = true;

            for (i = 0; i < pieces.length; i++) {
                if (!isNaN(pieces[i]) && (function (x) {
                        return (x | 0) === x;
                    })(parseFloat(pieces[i]))) {
                    if (pieces[i] < 0 || pieces[i] > 255) {
                        isValid = false;
                    }
                } else {
                    isValid = false;
                    break;
                }
            }
            return isValid;
        }
    }, 'Invalid IP address');

}
   function OnAdminButtonClick() {
        var source = $(this);
        $.ajax({
            url: '/refresh',
            data: JSON.stringify({
                'isshowrefresh': $(source).data('admin') == 'refresh',
                'isscan': $(source).data('admin') == 'scan'
            }),
            dataType: 'text',
            contentType: 'application/json',
            type: 'POST',
            error: function (req, errorString, ex) {
                showStatus(true, errorString)
                $('button, input').removeAttr('disabled');
                $('a').removeClass('disabled_link')
            },
            beforeSend: function () {
                $(source).find('.fa').addClass('fa-spin');
                $('button, input').attr('disabled', 'disabled');
                $('a').addClass('disabled_link');
            },
            success: function () {
                var successText;
                if ($(source).data('admin') == 'refresh') {
                    successText = 'Episodes refreshed from TVDB...';
                }
                else {
                    successText = 'Scanning complete...';
                }
                showStatus(false, successText)
                window.setTimeout(function () {
                    location.reload(true)
                }, 3000)
            }
        });
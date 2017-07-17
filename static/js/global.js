function Globals()
{
    $('[data-toggle="tooltip"]').tooltip();

    $('.admin').click(OnAdminClick)
}


function OnAdminClick() {
    dataAction = $(this).data('admin')
    $.ajax({
        url: '/refresh',
        data: JSON.stringify({
            'action': dataAction
        }),
        dataType: 'text',
        contentType: 'application/json',
        type: 'POST',
        error: function (req, errorString, ex) {
            showStatus(true, errorString)
        },
        beforeSend: function () {
            $('#scan-status').css('opacity',1.0);
            $('button, input').attr('disabled', 'disabled');
            $('a').addClass('disabled_link');
        },
        success: function () {
            var successText;
            if (dataAction == 'refresh') {
                successText = 'Episodes refreshed from TMDB...';
            } else {
                successText = 'Scanning complete...';
            }
            showStatus(false, successText)
            window.setTimeout(function () {
                location.reload(true)
            }, 3000)
        },
        complete: function() {
            $('#scan-status').css('opacity',0.0);
            $('button, input').removeAttr('disabled');
            $('a').removeClass('disabled_link');
        }
    });
}
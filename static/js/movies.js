function HandleMovieAction() {
    var action = $(this).data("movie-action");
    var id = $(this).data("movie-id");

    $.ajax({
        url: '/handle_movie',
        data: JSON.stringify({
            'movie_id': id,
            'movie_action': action,
        }),
        dataType: 'text',
        contentType: 'application/json',
        type: 'POST',
        beforeSend: function () {
            //animate and hide action icons
            //show spinner icon
        },
        error: function (req, errorString, ex) {
            showStatus(true, errorString);
        },
        success: function (data) {
            var ar = $.parseJSON($.parseJSON(data));
            if (ar.status == 'success') {
                if (action == 'ignore') {
                    $(source).closest('tr').remove();
                } else if (action = 'cleanup') {
                    location.reload(true);
                } else {
                    var currentRow = $(source).closest('tr');
                    var newText = $(currentRow).children().first().text() + ' is downloading..';
                    $(currentRow).children().remove();
                    $(currentRow).append('<td colspan="3" class="success">' + newText + '</td>');
                }
            } else {
                showStatus(ar.status.toLowerCase() == 'error', ar.message);
            }

        }
    })
}

function OnActionClick(){
    $(this).addClass('animated bounceOut')
    
}
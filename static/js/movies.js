function HandleMovieAction() {
    var action = $(this).data("movie-action");
    var id = $(this).data("movie-id");
    var button = this

    $.ajax({
        url: '/handle_movie',
        data: JSON.stringify({
            'movie_id': id,
            'movie_action': action,
        }),
        dataType: 'text',
        contentType: 'application/json',
        type: 'POST',
        beforeSend: OnActionClick(button),
        error: function (req, errorString, ex) {
            showStatus(true, errorString);
        },
        success: function (data) {
            var ar = $.parseJSON($.parseJSON(data));
            setTimeout(function () {
                if (ar.status == 'success') {
                    if (action == 'ignore') {
                        $(button).closest('.movie-row').slideUp().remove();
                    } else if (action == 'cleanup') {
                        location.reload(true);
                    } else {
                        var currentRow = $(button).closest('.movie-row');
                        $(currentRow).find('.movie-action-label span').addClass('text-success').text('Sent to jDownloader');
                        $(currentRow).find('.fa-spin').addClass('animated zoomOut');
                        setTimeout(function () {
                            $(currentRow).slideUp(300, function(){
                                $(this).remove()
                            })
                        }, 1000)
                    }
                } else {
                    showStatus(ar.status.toLowerCase() == 'error', ar.message);

                }
            }, 2500)
        }
    })
}



function OnActionClick(btn) {
    var actionButton = btn;
    var otherButton = $(btn).siblings('.btn').first();
    var label = $(btn).closest('h5').find('.movie-action-label');
    var message = $(btn).data('movie-action') == 'download' ? 'Downloading... ' : 'Removing... ';

    $(actionButton).addClass('animated bounceOut').tooltip('destroy');
    $(otherButton).addClass('animated flipOutX').tooltip('destroy');
    $(otherButton).one('webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend',
        function () {
            $(actionButton).parent().hide();
            $(label).find('span').text(message);
            $(label).css('display', 'inline').addClass('animated zoomIn');

        }
    )
    setTimeout(function () {

    }, 1000);
}

function OnIgnoreAllClick()
{
    movies = $('.movie-row')
    $.each(movies, function(i, e){
        $(e).find('[data-movie-action="ignore"]').click();
    })

    $(this).hide();
    //show block quote
}


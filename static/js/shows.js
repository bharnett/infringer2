var retrievedIcon = '<i class="fa fa-check-circle" style="color:#5cb85c" aria-hidden="true"></i>';
var pendingIcon = '<i class="fa fa-ellipsis-h" style="color:#f0ad4e" aria-hidden="true"></i>';



function OnShowClick() {
    $.each($("#episode-table").data("events"), function(i, event) {
        alert(i);
        $.each(event, function(j, h) {
            alert(h.handler);
        });
    });


    $.get('/show', { id: $(this).data('id') },
        function(data) {
            UpdateShow(data);
        });

    $('.show-link').removeClass('active');
    $(this).addClass('active');




}


function UpdateShow(data) {
    data = $.parseJSON(data);
    show = data[0];
    episodes = data[1];

    var img = new Image();
    img.src = show.background;
    var backgroundUrl = 'url("' + img.src + '")';




    var tb = $('#episode-table tbody');
    $('#episode-table').css('opacity', 0.0)
    $('#show-summary-section').css('opacity', 0.0)
    $('.page-bg').css('opacity', 0.0);

    $('#episode-table').one('webkitTransitionEnd otransitionend oTransitionEnd msTransitionEnd transitionend',
    function(e) {
        var cache =$('#show-name-header').children();
        $('#show-name-header').text(show.show_name).append(cache);
        $('#show-overview-paragraph').text(show.overview)
        $('#selected-show-id').data('id', show.show_id);

        $(tb).children().remove();

        episodes.forEach(function(episode) {
            var dlDate = '';
            var airDate =  '';

            if (episode.download_time != null) {
                var date = moment(episode.download_time)
                dlDate = date.format("ddd, MMM D, h:mm:ss a")
            }

            if (episode.air_date != null)
            {
                var aDate = moment(episode.air_date);
                air_date = aDate.format("ddd, MMM D");
            }

            var statusIcon = episode.status == 'Pending' ? pendingIcon : retrievedIcon;
            var episodeCode = ' (S' + ('0'+episode.season_number) + 'E' + ('0'+episode.episode_number) + ')';

            var nameCell = '<td class="col-md-4"><a href="#" data-id="' + episode.id + '" class="episode-link">' + episode.episode_name + episodeCode + '</a></td>';
            var dateCell = '<td class="col-md-2">' + air_date + '</td>';
            var dlCell = '<td class="col-md-2">' + dlDate + '</td>';
            var statusCell = '<td class="col-md-2">' + episode.status + ' ' + statusIcon + '</td>';
            var btn = '<td class="col-md-2"><button class="btn btn-xs btn-primary status-toggle" data-id="' + episode.id + '">Toggle Status</button></td>'

            var newRow = $(tb).append('<tr>').find('tr').last().append(nameCell).append(dateCell).append(dlCell).append(statusCell).append(btn);

        })

        //updates the URL
        //window.history.pushState(e.show_name, 'Title', '/shows/' + show.show_id);
        $('#episode-table').off('webkitTransitionEnd otransitionend oTransitionEnd msTransitionEnd transitionend');
        $('#episode-table').css('opacity', 1.0)
        $('#show-summary-section').css('opacity', 1.0)
        $('.page-bg').css('background-image', backgroundUrl).css('opacity', .35);

        $('.status-toggle').click(OnToggleClick);
        $('#show-name-header .btn').click(OnShowActionClick);
        $('[data-toggle="tooltip"]').tooltip();
        $('.episode-link').click(OnShowEpisodeClick);

        var targetEpisode = getParameterByName('episode_id')
        if (targetEpisode != null && targetEpisode != '')
        {
            var episodeRow = $('[data-id="' + targetEpisode + '"]').first().closest('tr')
            if (episodeRow.length > 0)
            {
                $('#table-section').scrollTo(episodeRow);
                $(episodeRow).addClass("animated bounce");
                $(episodeRow).find('a').click();
            }

        }

   });

}


function OnToggleClick()
{
    var source = $(this);
    $.ajax({
        url: '/update_episode',
        data: JSON.stringify({
            'id': $(source).data('id')
        }),
        dataType: 'text',
        contentType: 'application/json',
        type: 'POST',
        error: function (req, errorString, ex) {
            alert(errorString)
        },
        success: function (data) {
            d = $.parseJSON($.parseJSON(data));
            if (d == 'error') {
                showStatus(true, 'Error changing status')
            }
            else {
                var actionIcon = d == 'Pending' ? pendingIcon : retrievedIcon;

                $(source).closest('tr').find('i').parent().slideUp(300, function(){
                   $(this).html(d + ' ' + actionIcon);
                   $(this).slideDown();
                })

                }
            }
        });
}

function OnAllPendingClick()
{
    $('#episode-table tbody tr').each(function (i, e){
        var status = $(e).children().eq(3).text().trim();

        if (status == 'Retrieved')
        {
            $(e).find('.btn').click();
        }
    })
}

function OnShowActionClick()
{
        var id = $('#selected-show-id').val();
        var action = $(this).data('action');
        var button = $(this);

        $.ajax({
            url: '/update_show',
            dataType: 'text',
            contentType: 'application/json',
            data: JSON.stringify({
                'id': id,
                'action': action
            }),
            type: 'POST',
            beforeSend: OnActionClick(button),
            error: function (req, errorString, ex) {
                alert(errorString)
            },
            success: function (data) {
                if (data == 'error') {
                    alert("Error");
                }
                else {
                    showStatus(false, action == 'refresh' ? "Refresh completed.  Reloading page." : "Show removed.  Back to Index.")
                    window.setTimeout(function () {
                        action == 'refresh' ? window.location.reload('/show/' + id) : window.location.href = "/index";
                    }, 2000)
                }

            }
        });
}

function OnActionClick(btn) {
    var actionButton = btn;
    var otherButton = $(btn).siblings('.btn').first();
    var label = $('#show-action-label');
    var message = $(btn).data('action') == 'remove' ? 'Removing... ' : 'Refreshing... ';

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


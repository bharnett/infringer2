var retrievedIcon = '<i class="fa fa-check-circle" style="color:#5cb85c" aria-hidden="true"></i>';
var pendingIcon = '<i class="fa fa-ellipsis-h" style="color:#f0ad4e" aria-hidden="true"></i>';



function OnShowClick() {
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

    $('body').css('background-image', backgroundUrl);


    var tb = $('#episode-table tbody');
    $('#episode-table').css('opacity', 0.0)
    $('#show-summary-section').css('opacity', 0.0)

    $('#episode-table').one('webkitTransitionEnd otransitionend oTransitionEnd msTransitionEnd transitionend',
    function(e) {
        var cache =$('#show-name-header').children();
        $('#show-name-header').text(show.show_name).append(cache);
        $('#show-overview-paragraph').text(show.overview)
        $('#show-name-header').attr('data-id', show.show_id);

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


            var nameCell = '<td class="col-md-4"><a href="#" class="episode-link">' + episode.episode_name + '</a></td>';
            var dateCell = '<td class="col-md-2">' + air_date + '</td>';
            var dlCell = '<td class="col-md-2">' + dlDate + '</td>';
            var statusCell = '<td class="col-md-2">' + episode.status + ' ' + statusIcon + '</td>';
            var btn = '<td class="col-md-2"><button class="btn btn-xs btn-primary status-toggle" data-id="' + episode.id + '">Toggle Status</button></td>'

            var newRow = $(tb).append('<tr>').find('tr').last().append(nameCell).append(dateCell).append(dlCell).append(statusCell).append(btn);

        })
        $('#episode-table').css('opacity', 1.0)
        $('#show-summary-section').css('opacity', 1.0)

        $('.status-toggle').click(OnToggleClick);
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



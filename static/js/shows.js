function OnShowClick() {
    $.get('/show', { id: $(this).data('id') },
        function(data) {
            UpdateShow(data);
        });

    $('.show-link').removeClass('active');
    $(this).addClass('active');

}


function UpdateShow(data) {
    show = $.parseJSON(data);


    var img = new Image();
    img.src = show.background;
    var tb = $('#episode-table tbody');

    $(tb).children().remove();

    show.episodes.forEach(function(episode) {
        var dlDate = '';

        if (episode.download_time != null) {
            var date = moment(episode.download_time)
            dlDate = date.format("ddd, MMM D, h:mm:ss a")
        }


        var nameCell = '<td><a href="#" class="episode-link">' + episode.episode_name + '</a></td>';
        var dateCell = '<td>' + episode.air_date + '</td>';
        var dlCell = '<td>' + dlDate + '</td>';
        var statusCell = '<td>' + episode.status + '</td>';
        var btn = '<td><button class="btn btn-xs btn-primary">Toggle Status</button></td>'

        var newRow = $(tb).append('<tr>').find('tr').last().append(nameCell).append(dateCell).append(dlCell).append(statusCell).append(btn);

//        $(newRow).append('<td>').text(episode.name);
//        $(newRow).append('<td>').text(episode.air_date);
//        $(newRow).append('<td>').text(episode.download_time);
//        $(newRow).append('<td>').text(episode.status);

    })


}
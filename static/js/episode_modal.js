function OnShowEpisodeClick()
{
    var id = $(this).data('id');
    $.get('/episode', {id: id}, function(data){
        episode = $.parseJSON(data);
        var episodeCode = ' (S' + ('0'+episode.season_number) + 'E' + ('0'+episode.episode_number) + ')';

        $('.modal-header').text(episode.episode_name + episodeCode);
        $('.modal-header').text(episode.episode_name);
        $('#episode-detail-image').attr('src', episode.episode_image);
        $('#episode-detail-overview').text(episode.episode_description);
        $('#episode-detail-modal').modal('show');

        if (episode.is_downloaded)
        {
            var date = moment(episode.download_time)
            dlDate = date.format("ddd, MMM D, h:mm:ss a")
            $('#episode-detail-downloaded').text(dlDate);
            $('#episode-downloaded-section').show();
        }
        else {
            $('#episode-downloaded-section').hide();

        }

        if (episode.air_date != '')
        {
            var date = moment(episode.download_time)
            aDate = date.format("ddd, MMM D")
            $('#episode-detail-aired-date').text(aDate);
        }

            $('#episode-detail-parent').val(episode.parent_download_page);
            $('#episode-detail-source').val(episode.url_download_source);

            $('#episode-links-text').val(episode.download_links);
    });
}


function Validation()
{
 $('#episode-link-form').validate({
        highlight: function (element) {
            $(element).closest('.form-group').addClass("has-error");
        },
        unhighlight: function (element) {
            $(element).closest('.form-group').removeClass("has-error");
        },
        errorClass: 'control-label has-error',
        rules: {
            'episode-links-text': {
                required: true
        //                    remote: '/check_links',
            },
        },
        messages: {
            'episode-links-text': {
                remote: 'Links are invalid.'
            },

        },
        submitHandler: function (form) {
            var formData = $(form).serializeArray();
            var data = {};
            $(form).serializeArray().map(function (x) {
                data[x.name] = x.value;
            });
            var fromURL = $(form).attr('action');
            $.ajax({
                url: fromURL,
                type: 'POST',
                data: JSON.stringify(data),
                dataType: 'text',
                contentType: 'application/json',
                error: function (jqXHR, textStatus, errorThrown) {
                    showStatus(true, textStatus + ' ' + errorThrown);
                },
                success: function (data) {
                    var ar = $.parseJSON($.parseJSON(data));
                    showStatus(ar.status == 'error', ar.message);

                }
            });
        }
        });


}
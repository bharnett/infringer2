function SetupTVPopover(e) {

    element = $(e)
    var name, overview, poster, id, counter;
    name = $(element).data('name');
    overview = $(element).data('overview');
    id = $(element).data('id');
    poster = $(element).data('poster');
    showName = $(element).data('show-name');
    episodeId = $(element).data('episode-id');
    actionRow = ''
    var titleText = ''
    var placementOption = 'right auto'
    var isAddable = $(e).hasClass('addable');
    var containerOption = ''

    if (isAddable) {
        titleText = name;
        actionRow = '<div class="row"><div class="col-xs-12">' +
            '<button style="margin-top: 10px;" class="btn btn-block btn-xs btn-primary addable-button" data-id="' + id + '">Add ' +
            '<i class="fa fa-spinner fa-spin" style="display:none;" aria-hidden="true"></i></button>' +
            '</div></div>'
        placementOption = 'left auto'
        containerOption = 'body'

    } else {
        titleText = '<a href="/shows/' + id + '">' + showName + '</a> - <a href="/shows/' + id + '?episode_id=' + episodeId + '">' + name + '</a>';
    }

    var img = new Image();
    img.src = poster;

    $(element).popover({
        container: 'body',
        placement: placementOption,
        trigger: 'manual',
        html: true,
        delay: {
            "hide": 300
        },
        title: titleText,
        content: '<div class="row"><div class="col-xs-3">' +
        '<img class="img-responsive img-rounded" src="' + poster + '"></div>' +
        '<div class="col-xs-9"><p>' + overview + '</p></div></div>' + actionRow
    }).on('click', function () {
        var _this = this;
        $(this).popover("show");
        $('.popover').find('.addable-button').click(OnShowAddClick)
        $(".popover").add(_this).on("mouseleave", function () {
            setTimeout(function () {
                if (!$(".popover:hover").length) {
                    $(_this).closest('.row-scroll-section').removeClass('addable-popover');
                    $(_this).popover("hide");
                    $('popover').find('.addable-button').off('click', OnShowAddClick)
                }
            }, 300)            
        });
        $(_this).closest('.row-scroll-section').addClass('addable-popover');

    })

    // .on("click", function () {
    //     var _this = this;

    //     setTimeout(function () {
    //         if (!$(".popover:hover").length) {
    //             $(_this).popover("hide");
    //         }
    //     }, 300);

    // });
}
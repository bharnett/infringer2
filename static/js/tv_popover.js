function SetupTVPopover(e) {

    element = $(e)
    var name, overview, poster, id, counter;
    name = $(element).data('name');
    overview = $(element).data('overview');
    id = $(element).data('id');
    poster = $(element).data('poster');
    actionRow = ''
    var titleText = ''
    if ($(e).hasClass('addable')) {
        titleText = name;
        actionRow = '<div class="row"><div class="col-xs-12">' + 
        '<button style="margin-top: 10px;" class="btn btn-block btn-xs btn-primary addable-button" data-id="' + id +'">Add ' + 
        '<i class="fa fa-spinner fa-spin" style="display:none;" aria-hidden="true"></i></button>' + 
        '</div></div>'

    } else {
        titleText = '<a href="/show/' + id + '">' + name + '</a>';
    }


    // if (source == 'this week')
    // {
    //     // only shows from this week section of the index.html page

    // }
    // else {
    //     // this is for shows that are on the popular or premier section
    // }
    var img = new Image();
    img.src = poster;

    $(element).popover({
        container: 'body',
        placement: 'top',
        trigger: 'manual',
        html: true,
        delay: {
            "hide": 300
        },
        title: titleText,
        content: '<div class="row"><div class="col-xs-3">' +
            '<img class="img-responsive img-rounded" src="' + poster + '"></div>' +
            '<div class="col-xs-9"><p>' + overview + '</p></div></div>' + actionRow
    }).on("mouseenter", function () {
        var _this = this;
        $(this).popover("show");
        $('.popover').find('.addable-button').click(OnShowAddClick)
        $(".popover").on("mouseleave", function () {
            $(_this).popover('hide');
        });
    }).on("mouseleave", function () {
        var _this = this;
        $('popover').find('.addable-button').off('click', OnShowAddClick)
        setTimeout(function () {
            if (!$(".popover:hover").length) {
                $(_this).popover("hide");
            }
        }, 300);

    });
}
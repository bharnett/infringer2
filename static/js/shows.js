function OnShowClick()
{
    $.get('/show',
        {id: $(this).data('id') },
        function(data){
            UpdateShow(data);
        });


}


function UpdateShow(data)
{
    show = $.parseJSON(data);


    var img = new Image();
    img.src = show.background;
    $('body').css('background', 'url(' + img.src + ') no-repeat center center fixed');



}
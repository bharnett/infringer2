function HandleSearchAndAdd() {
    $('#search-button').click(OnSearchClick)
    $("#show-search-input").keypress(function (e) {
        if (e.which == 13) {
            e.preventDefault();
            $("#search-button").click();
        }
    });
}

// function OnSearchClick() {
//     text = $('#show-search-input').val();

//     $(this).find('i').toggle();
//     $.get('/search', {
//             show_search: text
//         },
//         function (data) {
//             $('#search-results-table tbody tr').remove(); //remove all existing rows before adding
//             var results = $.parseJSON(data);
//             $.each(results, function (i, val) {
//                 $('#search-results-table tbody').append('<tr></tr>');
//                 var row = $('#search-results-table tr:last');
//                 $(row).append('<td>' + val.name + '</td>');
//                 $(row).append('<td>' + val.premier_date + '</td>');
//                 $(row).append('<td>' + val.network + '</td>');
//                 $(row).append('<td><button type="button" class="btn btn-info btn-xs" data-series-id="' +
//                     val.id + '">Add <i class="fa fa-spinner fa-spin" style="display:none;" aria-hidden="true"></i></button></td>');

//             });
//             $('#add-show-modal').modal();
//             $('#search-results-table button').click(OnShowAddClick);
//             $(this).find('i').toggle();



//         });
// }

function OnSearchClick() {
    text = $('#show-search-input').val();
    btn = $(this);

    if (text.trim() == '') {
        return false;
    }
    $.ajax({
        url: '/search',
        data: {
            show_search: text
        },
        beforeSend: function () {
            $(btn).find('i').toggle();
            $('#show-search-input, #search-button').attr('disabled', 'disabled');
        },
        dataType: 'text',
        contentType: 'application/json',
        type: 'GET',
        error: function (req, errorString, ex) {
            showStatus(true, errorString)
        },
        success: function (data) {
            $('#search-results-table tbody tr').remove(); //remove all existing rows before adding
            var results = $.parseJSON($.parseJSON(data));
            $.each(results, function (i, val) {
                $('#search-results-table tbody').append('<tr></tr>');
                var row = $('#search-results-table tr:last');
                $(row).append('<td>' + val.name + '</td>');
                $(row).append('<td>' + val.premier_date + '</td>');
                $(row).append('<td>' + val.network + '</td>');
                $(row).append('<td><button type="button" class="btn btn-info btn-xs" data-series-id="' +
                    val.id + '">Add <i class="fa fa-spinner fa-spin" style="display:none;" aria-hidden="true"></i></button></td>');

            });
            $('#add-show-modal').modal();
            $('#search-results-table button').click(OnShowAddClick);
        },
        complete: function (data) {
            $(btn).find('i').toggle();
            $('#show-search-input, #search-button').removeAttr('disabled');


        }

    })

}



function OnShowAddClick() {
    var id = $(this).data('series-id');
    var btn = $(this);
    var data = {
        'series_id': id
    }
    $.ajax({
        url: '/add_show',
        data: JSON.stringify(data),
        beforeSend: function () {
            $(btn).find('i').toggle();
            $('#add-show-modal .btn').attr('disabled', 'disabled');
        },
        dataType: 'text',
        contentType: 'application/json',
        type: 'POST',
        error: function (req, errorString, ex) {
            showStatus(true, errorString)
        },
        success: function (data) {
            if (data == 'duplicate') {
                showStatus(true, 'Show already exists!')
            } else {
                window.location.href = "/show/" + id
            }
        },
        complete: function (data) {
            $('#add-show-modal .btn').removeAttr('disabled');
            $(btn).find('i').toggle();
        }

    })
}
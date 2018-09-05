function voteAnswer(val, id) {
    $.ajax({
        url: '/ajax/',
        type: 'post',
        data: 'route=catalog/get-brands-list&ids=' + list + '&sid=' + sec + '&word=' + word,
        success: function (data, textStatus) {
            eval(data);

        }
    });
}

$(".answer_vote.up_arrow").click(function() {
    id=$(this).attr("data-id");
    voteAnswer('up', id);
});

$(".answer_vote.down_arrow").click(function() {
    id=$(this).attr("data-id");
    voteAnswer('down', id);
});
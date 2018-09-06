function makeVote(type, val, id) {
    $.ajax({
        url: '/question/vote/',
        type: 'get',
        data: 'type=' + type + '&id=' + id + '&value=' + val,
        success: function (data, textStatus) {
            alert(data);

        }
    });
}

$(".answer_vote.up_arrow").click(function() {
    id=$(this).attr("data-id");
    makeVote('answer','up', id);
});

$(".answer_vote.down_arrow").click(function() {
    id=$(this).attr("data-id");
    makeVote('answer','down', id);
});
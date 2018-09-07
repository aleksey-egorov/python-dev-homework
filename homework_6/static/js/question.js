function makeVote(type, val, id) {
    $.ajax({
        url: '/question/vote/',
        type: 'get',
        data: 'type=' + type + '&id=' + id + '&value=' + val,
        success: function (data, textStatus) {
            var Result = '';
            eval(data);

            var votes = $("#" + type + "_" + id + " .votes span");
            var up = $("#" + type + "_" + id + " .up_arrow");
            var down = $("#" + type + "_" + id + " .down_arrow");
            if (val == 'up') {
                current = up;
            } else {
                current = down;
            }

            if (Result == 'add' || Result == 'update') {
                 up.removeClass("active");
                 down.removeClass("active");
                 current.addClass('active');
                 votes.html(Votes)
            }
            else if (Result == 'delete') {
                 current.removeClass('active');
                 votes.html(Votes)
            }
            else if (Result == 'error') {
                alert('error making vote');
            }
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

$(".quest_vote.up_arrow").click(function() {
    id=$(this).attr("data-id");
    makeVote('question','up', id);
});

$(".quest_vote.down_arrow").click(function() {
    id=$(this).attr("data-id");
    makeVote('question','down', id);
});
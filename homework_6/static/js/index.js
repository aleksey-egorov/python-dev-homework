$("#question_filter a").click(function() {
    if (!($(this).hasClass("active"))) {
        $("#question_filter a").removeClass("active");
        $(this).addClass("active");

        var sort = $(this).attr("data-type");
        var page = $("#page").val();

        $.ajax({
            url: '/question/list/',
            type: 'get',
            data: 'sort=' + sort + '&page=' + page,
            success: function (data, textStatus) {
                var Result = '';

                $("#questions_content").html(data);

            }
        });
    }
});
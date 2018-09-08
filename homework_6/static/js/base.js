$("#main_search_form").submit(function(e) {
    e.preventDefault();
    var query=$("#main_search").val();
    var regexp = /tag\:[(\s\w)+]/g;
    if (regexp.test(query)) {
        var words = query.split(":");
        var word = $.trim(words[1]);
        location.href = "/tag/" + word + "/";
    } else {
        location.href = "/search/?q=" + query;
    }

});
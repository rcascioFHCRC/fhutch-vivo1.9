$(document).ready(function () {
    $('ul.tree').hide();
    $('span.tree-toggler').click(function () {
        $(this).parent().children('ul.tree').toggle(200);
        if ($(this).hasClass('bottom') == true) {
            $(this).removeClass('bottom');
            $(this).addClass('left');
        } else {
            $(this).removeClass('left');
            $(this).addClass('bottom');
        }
    });
});

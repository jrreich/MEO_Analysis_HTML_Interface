$(document).ready(function () {
    $("table td.ant_percent_table").each(function () {
        var content = $(this).html();
        var red;
        var green;

        if (content === 0) {
            $(this).css('background-color', '#00FF00');
        } else {
            if (content > 0.5) {
                red = 255;
                green = parseInt(-2 * 255 * content + (2 * 255));
            } else {
                green = 255;
                red = parseInt(2 * 255 * content);
            }
            var rgbColor = 'rgb(' + red + ',' + green + ', 0)';
            $(this).css('background-color', rgbColor);
        }
    });
});
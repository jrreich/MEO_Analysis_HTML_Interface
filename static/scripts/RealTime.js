$(document).ready(function () {
    $("table td.ant_percent_table").each(function () {
        var content = $(this).html();
        var red;
        var green;

        if (content === 0) {
            $(this).css('background-color', '#666666');
        } else {
            if (content > 80) {
                green = 255;
                red = 0;
            } else if (content > 50) {
                red = 255;
                green = parseInt(2 * 255 * content);
            } else {
                red = 255;
                green = 0;

            }
            var rgbColor = 'rgb(' + red + ',' + green + ', 0)';
            $(this).css('background-color', rgbColor);
        }
    });
});
var speeds = {
    'fl': 0,
    'ml': 0,
    'bl': 0,
    'fr': 0,
    'mr': 0,
    'br': 0
};
function setProgress(motor, val) {
    var element = $('#'+motor);
    var text = $('#'+motor+'-text');
    if (val < 0) {
        element.css('background-color', 'red');
    } else {
        element.css('background-color', 'lawngreen');
    }
    val = Math.abs(val);
    $({deg: speeds[motor]}).stop().animate({deg: val}, {
        duration: 250,
        step: function(now) {
            element.css({
                height: now+'%'
            });
            text.text(Math.round(now));
        }
    });
    speeds[motor] = val;
}
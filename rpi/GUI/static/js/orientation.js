$(document).ready(function() {
    createHeadingText();
    rotate(360);
    generateHLines();
});

function createHeadingText() {
    var circle = $('#heading-circle');
    for(i=0;i<360;i+=10) {
        circle.append('<span class="rotated-heading" id="'+i+'">'+i+'</span>');
        var e = $('#'+i);
        e.css('-ms-transform', 'rotate('+i+'deg)');
        e.css('-webkit-transform', 'rotate('+i+'deg)');
        e.css('transform', 'rotate('+i+'deg)');
    }
}

function generateHLines() {
    var monitor = $('#lines-container');
    for(i=-90;i<91;i+=10) {
        monitor.append(
        '<div id="a">'+
            '<div style="width: 30%; background-color: white; top: 50%; height: 3px; margin-top: '+ i*2 +'%; margin-left: 35%; position: absolute;">'+
                '<span style="position: absolute; right: 103%; font-size: 1.5vw; font-weight: bold; top: -0.75vw;color: #fff;">'+-i+'</span>' +
                '<span style="position: absolute; margin-left: 53%; font-size: 1.5vw; font-weight: bold; top: -0.75vw;color: #fff;">'+-i+'</span>' +
            '</div>' +
        '</div>');
    }
    for(i=-90;i<91;i+=5) {
        monitor.append(
        '<div id="a">'+
            '<div style="width: 15%; background-color: white; top: 50%; height: 2px; margin-top: '+ i*2 +'%; margin-left: 42.5%; position: absolute;"></div>' +
        '</div>');
    }
    for(i=-90;i<91;i+=1) {
        monitor.append(
        '<div id="a">'+
            '<div style="width: 3%; background-color: white; top: 50%; height: 1px; margin-top: '+ i*2 +'%; margin-left: 48.5%; position: absolute;"></div>' +
        '</div>');
    }

}

function rotate(angle) {
    var $elem = $('#heading-circle');
    $({deg: 0}).animate({deg: angle}, {
        duration: 1000,
        step: function(now) {
            $elem.css({
                transform: 'rotate(' + now + 'deg)'
            });
        }
    });
}


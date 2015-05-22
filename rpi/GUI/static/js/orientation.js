var current_rotation = 0;
var current_roll = 0;

$(document).ready(function() {
    createHeadingText();
    generateHLines();
    setRoll(0);
    setHeading(0);
});

function createHeadingText() {
    var circle = $('#heading-circle');
    for(i=0;i<360;i+=10) {
        circle.append('<span class="rotated-heading" id="'+i+'">'+i+'</span>');
        var e = $('#'+i);
        e.css('-ms-transform', 'rotate('+i+'deg)');
        e.css('-moz-transform', 'rotate('+i+'deg)');
        e.css('-webkit-transform', 'rotate('+i+'deg)');
        e.css('transform', 'rotate('+i+'deg)');
    }
}

function createRollText() {
    var scale = $('#roll-scale');
    for(i=-60;i<61;i+=10) {
        scale.append('<span class="rotated-heading" id="'+i+'">'+i+'</span>');
        var e = $('#'+i);
        e.css('-ms-transform', 'rotate('+i+'deg)');
        e.css('-moz-transform', 'rotate('+i+'deg)');
        e.css('-webkit-transform', 'rotate('+i+'deg)');
        e.css('transform', 'rotate('+i+'deg)');
    }
}

function generateHLines() {
    var monitor = $('#lines-container');
    for(i=-90;i<91;i+=10) {
        monitor.append(
        '<div id="a">'+
            '<div style="width: 30%; background-color: white; top: 50%; height: 0.2vw; margin-top: '+ i*2 +'vh; margin-left: 35%; position: absolute;">'+
                '<span style="position: absolute; right: 103%; font-size: 1.5vw; font-weight: bold; top: -0.75vw;color: #fff;">'+-i+'</span>' +
                '<span style="position: absolute; margin-left: 53%; font-size: 1.5vw; font-weight: bold; top: -0.75vw;color: #fff;">'+-i+'</span>' +
            '</div>' +
        '</div>');
    }
    for(i=-90;i<91;i+=5) {
        monitor.append(
        '<div id="a">'+
            '<div style="width: 15%; background-color: white; top: 50%; height: 0.15vw; margin-top: '+ i*2 +'vh; margin-left: 42.5%; position: absolute;"></div>' +
        '</div>');
    }
    for(i=-90;i<91;i+=1) {
        monitor.append(
        '<div id="a">'+
            '<div style="width: 3%; background-color: white; top: 50%; height: 1px; margin-top: '+ i*2 +'vh; margin-left: 48.5%; position: absolute;"></div>' +
        '</div>');
    }
}

function setRoll(angle) {
    var $elem = $('#monitor-bg');
    $({deg: current_roll}).stop().animate({deg: angle}, {
        duration: 500,
        step: function(now) {
            $elem.css({
                transform: 'rotate(' + now + 'deg)'
            });
        }
    });
    current_roll = angle;
}

function setPitch(angle){
    var $elem = $('#lines-container');
    $elem.stop().animate({top: angle*2+'vh'});

}

function setHeading(angle) {
    var $elem = $('#heading-circle');
    var target = 0;
    if (Math.abs(-current_rotation - angle) > 180) {
        target = angle - 360;
    } else {
        target = angle;
    }
    var duration = 1000;
    if((-current_rotation - angle) == 360) {
        duration = 0
    }
    $({deg: current_rotation}).stop().animate({deg: -target}, {
        duration: duration,
        step: function(now) {
            $elem.css({
                transform: 'rotate(' + (now)+ 'deg)'
            });
            if(-now < 0) {
                $('#heading-text').text(Math.round(360-now));
            } else {
                $('#heading-text').text(Math.round(-now));
            }

        }
    });
    current_rotation = -target;
    console.log(-angle)
}


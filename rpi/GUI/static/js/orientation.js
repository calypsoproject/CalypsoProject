$(document).ready(function() {
    createHeadingText();
    rotate(45);
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

function rotate(angle) {
    var $elem = $('#heading-circle');

    $({deg: 0}).animate({deg: angle}, {
        duration: 2000,
        step: function(now) {
            $elem.css({
                transform: 'rotate(' + now + 'deg)'
            });
        }
    });
}


var current_roll = 0;
var current_pitch = 0;
var roll_animation = null;
var pitch_animation = null;
var animation_duration = 200;
var framerate = 30;
var y_translate = -15;
var x_translate = 30;

$(document).ready(function() {
    cv = $('#cv');

    viewer = new JSC3D.Viewer(document.getElementById('cv'));
    viewer.setParameter('SceneUrl', 'js/calypso.obj');
    viewer.setParameter('ModelColor',       '#cbcbcb');
    viewer.setParameter('BackgroundColor1', '#141E2D');
    viewer.setParameter('BackgroundColor2', '#141E2D');
    viewer.setParameter('RenderMode',       'wireframe');
    viewer.setParameter('Definition', 'high');
    viewer.setParameter('InitRotationX', 	0);
    viewer.setParameter('InitRotationY', 	-90);
    viewer.setParameter('InitRotationZ', 	0);
    viewer.init();
    viewer.update();
    onResize()
});

$(window).resize(function(){
    onResize();
});

function onResize() {
    var w = $(document).width();
    var h = $(document).height();
    if (w < h) {
        cv.width(w);
    } else {
        cv.width(h);
    }
}

function setRoll(angle) {
    var rotation = angle - current_roll;
    var step = (rotation / (animation_duration*framerate/1000)) ;
    clearInterval(roll_animation);
    roll_animation = setInterval(function () {
        if(Math.round(angle)==Math.round(current_roll)) {
            clearInterval(roll_animation);
        } else {
            viewer.rotate(-y_translate, 0, 0);
            viewer.rotate(0, x_translate, 0);
            viewer.rotate(0, 0, -step);
            viewer.rotate(0, -x_translate, 0);
            viewer.rotate(y_translate, 0, 0);
            current_roll += step;
            viewer.update();
        }
    }, (1/framerate)*1000);
}

function setPitch(angle) {
    var rotation = angle - current_pitch;
    var step = (rotation / (animation_duration*framerate/1000)) ;
    clearInterval(pitch_animation);
    pitch_animation = setInterval(function () {
        if(Math.round(angle)==Math.round(current_pitch)) {
            clearInterval(pitch_animation);
        } else {
            viewer.rotate(-y_translate, 0, 0);
            viewer.rotate(0, x_translate, 0);
            viewer.rotate(step, 0, 0);
            viewer.rotate(0, -x_translate, 0);
            viewer.rotate(y_translate, 0, 0);
            current_pitch += step;
            viewer.update();
        }
    }, (1/framerate)*1000);
}
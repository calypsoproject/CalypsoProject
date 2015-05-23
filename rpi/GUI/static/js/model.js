$(document).ready(function() {
    cv = $('#cv');

    viewer = new JSC3D.Viewer(document.getElementById('cv'));
    viewer.setParameter('SceneUrl', 'js/calypso.obj');
    viewer.setParameter('ModelColor',       '#cbcbcb');
    viewer.setParameter('BackgroundColor1', '#141E2D');
    viewer.setParameter('BackgroundColor2', '#141E2D');
    viewer.setParameter('RenderMode',       'smooth');
    viewer.setParameter('Definition', 'high');
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
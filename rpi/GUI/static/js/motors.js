/**
 * Created by zigapk on 5/21/15.
 */

function onResize() {
    scrw = $("html").width();

    var h = document.getElementById("podmornica").clientHeight;
    var str = (h).toString() + "px";
    document.getElementById("content").style.height = str;
    var w = document.getElementById("podmornica").clientWidth;
    str = w.toString() + "px";
    document.getElementById("content").style.width = str;

    var pheight = Math.floor(h*0.16);
    var pwidth = Math.floor(pheight*0.45);
    $(".progress").width(pheight);
    $(".progress-item").width(pheight);
    $(".progress").height(pwidth);
    var fsize = Math.round(0.8*pwidth)
    $(".progress-item").css("fontSize", fsize);

    var leftProgMargin = $(".rel1").offset()["left"] + pwidth + Math.round(document.getElementById("podmornica").clientWidth * 0.7);
    $(".right").css("left", leftProgMargin);
    $(".right-item").css("left", leftProgMargin);
    $(".progress-text-right").css("left", leftProgMargin);

}

function setProgress(motor, val){
    var id = "";
    var pid = "";
    if(motor == "fl") {
        id = "motor-1";
        pid = "motor-1-p";
    } else if(motor == "ml") {
        id = "motor-2";
        pid = "motor-2-p";
    } else if(motor == "bl") {
        id = "motor-3";
        pid = "motor-3-p";
    } else if(motor == "fr") {
        id = "motor-4";
        pid = "motor-4-p";
    } else if(motor == "mr") {
        id = "motor-5";
        pid = "motor-5-p";
    } else if(motor == "br") {
        id = "motor-6";
        pid = "motor-6-p";
    }
    //setProgress(document.getElementById(id), document.getElementById(pid), val)
    document.getElementById(id).setAttribute("value", val);
    document.getElementById(pid).textContent = val.toString();
}

/*function setProgress(element, text, val) {
    $({deg: element.getAttribute('value')}).animate({deg: val} {
        duration: 1000,
        step: function(now) {
            element.
        }
    });
}*/

onResize();
var n = 0;
$(document).ready(function () {
    setInterval(function(){
        update();
    }, 100);
});

function update() {
    log(0, Date.now());
    log(1, Date.now());
    log(2, Date.now());
}

function scroll() {
    $(document).scrollTop($(document).height());
}

function log(level, message) {
    var color;
    if(level==0 && infoToggled) {
        level = "info";
        color = "#33D42B";
    } else if(level==1 && warningToggled) {
        level = "warning";
        color = "#FFC108";
    } else if(errorToggled) {
        level = "error";
        color = "#FF3308";
    }
    if (typeof level == typeof 1) {return;}
    $('#logger').append("<terminal-line id=\""+n+"\">CalypsoProject <log-level style=\"color: "+color+";\">("+level+")</log-level>:~$ <log-message>"+message+"</log-message><br></terminal-line>");
    $('#'+(n-100)).remove();
    scroll();
    n++;
}

var infoToggled = true;
function infoOnClick() {
    if (infoToggled) {
        $('#info').css("background-color", "#666");
        infoToggled = false;
    } else {
        $('#info').css("background-color", "#333");
        infoToggled = true;
    }

}
var warningToggled = true;
function warningOnClick() {
    if (warningToggled) {
        $('#warning').css("background-color", "#666");
        warningToggled = false;
    } else {
        $('#warning').css("background-color", "#333");
        warningToggled = true;
    }

}
var errorToggled = true;
function errorOnClick() {
    if (errorToggled) {
        $('#error').css("background-color", "#666");
        errorToggled = false;
    } else {
        $('#error').css("background-color", "#333");
        errorToggled = true;
    }

}



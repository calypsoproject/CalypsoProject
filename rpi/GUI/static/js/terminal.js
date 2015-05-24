var n = 0;

function scroll() {
    $(document).scrollTop($(document).height());
}

function log(level, origin, message) {
    var color;
    if(level==0 && infoToggled) {
        level = "info";
        color = "#33D42B";
    } else if(level==1 && warningToggled) {
        level = "warning";
        color = "#FFC108";
    } else if(level==2 && errorToggled) {
        level = "error";
        color = "#FF3308";
    } else if(level==3 && verboseToggled) {
        level = "verbose";
        color = "#a4ff95";
    }

    if (typeof level == typeof 1) {return;}
    $('#logger').append("<terminal-line id=\""+n+"\">"+origin+"<log-level style=\"color: "+color+";\">("+level+")</log-level>:~$ <log-message>"+message+"</log-message><br></terminal-line>");
    $('#'+(n-100)).remove();
    scroll();
    n++;
}

var verboseToggled = false;
function verboseOnClick() {
    if (verboseToggled) {
        $('#verbose').css("background-color", "#141E2D");
        verboseToggled = false;
    } else {
        $('#verbose').css("background-color", "#030A13");
        verboseToggled = true;
    }

}

var infoToggled = true;
function infoOnClick() {
    if (infoToggled) {
        $('#info').css("background-color", "#141E2D");
        infoToggled = false;
    } else {
        $('#info').css("background-color", "#030A13");
        infoToggled = true;
    }

}
var warningToggled = false;
function warningOnClick() {
    if (warningToggled) {
        $('#warning').css("background-color", "#141E2D");
        warningToggled = false;
    } else {
        $('#warning').css("background-color", "#030A13");
        warningToggled = true;
    }

}
var errorToggled = false;
function errorOnClick() {
    if (errorToggled) {
        $('#error').css("background-color", "#141E2D");
        errorToggled = false;
    } else {
        $('#error').css("background-color", "#030A13");
        errorToggled = true;
    }

}



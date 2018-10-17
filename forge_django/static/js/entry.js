var MyVars = {
    keepTrying: true
};

$(document).ready(function () {

    console.log('location.href =' + location.href)

    commonInitialize()

   if(location.href.includes("/forge-home/")){
        console.log("case : /forge-home/")

        //do something
    }

});

function commonInitialize() {

    // hide elements specified by django template engine.
    $(".django-hide").hide()
    return;
}






function loadViewer(token, expires_in, urn){
    //initialize viewr
    //var defaultid =  $.cookie("defaulturn");
    //var urn = base64encode(defaultid);
    MyVars.token = token;
    MyVars.expires_in = expires_in;

    encoded_urn = base64encode(urn)
    console.log('urn =' + urn)
    console.log('encoded_urn =' + encoded_urn)
    initializeViewer(encoded_urn);

    //switch loading to regular
    //$("#loading").fadeOut();
    //$("#container-ec").fadeIn();
}

function base64encode(str) {
    var ret = "";
    if (window.btoa) {
        ret = window.btoa(str);
    } else {
        // IE9 support
        ret = window.Base64.encode(str);
    }

    // Remove ending '=' signs
    // Use _ instead of /
    // Use - insteaqd of +
    // Have a look at this page for info on "Unpadded 'base64url' for "named information" URI's (RFC 6920)"
    // which is the format being used by the Model Derivative API
    // https://en.wikipedia.org/wiki/Base64#Variants_summary_table
    var ret2 = ret.replace(/=/g, '').replace(/[/]/g, '_').replace(/[+]/g, '-');

    console.log('base64encode result = ' + ret2);

    return ret2;
}

function loadJsTree(){
    console.log('loadJsTree [start]');
    $('#js-tree').jstree();
}

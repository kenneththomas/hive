function generateFix() {
    console.log('generating fix message');
    var basefix = '8=DFIX;35=D',
        tailfix = ';10=END',
        tag49 = ';49=' + document.getElementById("sendercompid").value,
        tag56 = ';56=' + document.getElementById("targetcompid").value,
        tag55 = ';55=' + document.getElementById("symbol").value,
        tag54 = ';54=' + document.getElementById("side").value,
        tag11 = ';11=' + clordid(),
        tag38 = ';38=' + document.getElementById("orderqty").value,
        tag40 = ';40=' + document.getElementById("ordertype").value,
        tag1 = ';1=' + document.getElementById("traderid").value
    if (tag40 == ";40=1") {
        newfix = basefix + tag49 + tag56 + tag11 + tag1 + tag55 + tag54 + tag38 + tag40 + tailfix;
    } else {
        tag44 = ';44=' + document.getElementById("price").value,
            newfix = basefix + tag49 + tag56 + tag11 + tag1 + tag55 + tag54 + tag38 + tag40 + tag44 + tailfix;
    };
    document.getElementById("generated").value = newfix;
}
//this shows the price tab if it's a limit order
function isLimit() {
    console.log('running isLimit');
    var ordertype = document.getElementById("ordertype").value;
    if (ordertype == 2) {
        //unhide price
        document.getElementById("pricer").style.visibility = 'visible';
    } else {
        document.getElementById("pricer").style.visibility = 'hidden';
    }
}
//generate uuid for tag 11
function clordid() {
    function s4() {
        return Math.floor((1 + Math.random()) * 0x10000)
            .toString(16)
            .substring(1);
    }
    return s4() + '-' + s4(); 
}

//websocket stuff below, WIP
var fixserver = new WebSocket("ws:127.0.0.1:20001");

fixserver.sendFix = function(){
    //check if we are connected and only send if we are connected
    if (fixserver.readyState == 1) {
        //get generated fixmessage
        var outgoingfix = document.getElementById("generated").value;
        console.log("outgoing fix: " + outgoingfix);
        //send it to the socket
        fixserver.send(outgoingfix);
    } else {
        document.getElementById("execreport").innerHTML = "not connected to server"
    }
};

//whenever we get something from the fixserver
fixserver.onmessage = function(event) {
    var execreport = event.data;
    console.log('received from server: ' + execreport);
    document.getElementById("execreport").innerHTML = execreport;
};

//login
// Get the modal
var modal = document.getElementById('id01');

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}
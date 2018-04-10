function generateFix() {
    console.log('generating fix message');
    var basefix = '8=DFIX;35=D'
    var tailfix = ';55=ZVZZT;54=1;40=1;10=END'
    var tag49 = ';49=' + document.getElementById("sendercompid").value;
    var tag56 = ';56=' + document.getElementById("targetcompid").value;
    var newfix = basefix + tag49 + tag56 +  tailfix
    document.getElementById("generated").innerHTML = newfix;
}
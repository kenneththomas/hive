function generateFix() {
    console.log('generating fix message');
    var basefix = '8=DFIX;35=D',
        tailfix = ';54=1;40=1;10=END',
        tag49 = ';49=' + document.getElementById("sendercompid").value,
        tag56 = ';56=' + document.getElementById("targetcompid").value,
        tag55 = ';55=' + document.getElementById("symbol").value,
        tag54 = ';54=' + document.getElementById("side").value;
        newfix = basefix + tag49 + tag56 + tag55 + tag54 + tailfix;
        document.getElementById("generated").innerHTML = newfix;
}
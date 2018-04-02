//to become "exchange" which will receive orders from hive pyengine and execute them

val fixmsg = "8=DUMFIX;11=4a4964c6;49=Tay;56=Spicii;35=D;55=ZVZZT;54=1;38=100;44=10;40=2;10=END"

fun main(args: Array<String>) {
    println("printing fix msg")
    println(fixmsg)
    println("parsing fix msg")
    val fixmap = fixmsg.split(";").map { it.split("=") }.associate { Pair(it[0], it[1]) }
    println(fixmap)
}

/* for future reference if we want to retrieve a fix value from the map, we can do this with
fixmap.get("35")
 */
import uuid

def neworder():
    tag11 = str(uuid.uuid1())[:8]
    fixmsg = {
        8 : 'DUMFIX',
        11 : tag11,
        49 : 'Tay',
        56 : 'Spicii',
        35 : 'D',
        55 : 'AAPL',
        54 : 1,
        38 : 100,
        44 : 170,
        40 : 2,
              }
    genfix = ''
    for key,val in fixmsg.items():
        #print(str(key) + '=' + str(val) + ';',end="")
            genfix = genfix + str(key) + "=" + str(val) + ';'
    return genfix

print(neworder())

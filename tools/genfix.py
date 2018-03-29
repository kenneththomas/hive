import uuid
import collections

def neworder():
    tag11 = str(uuid.uuid1())[:8]
    fixmsg = collections.OrderedDict({
        '8' : 'DUMFIX',
        '11' : tag11,
        '49' : 'Tay',
        '56' : 'Spicii',
        '35' : 'D',
        '55' : 'ZVZZT',
        '54' : '1',
        '38' : '100',
        '44' : '10',
        '40' : '2',
              })
    genfix = ''
    for key,val in fixmsg.items():
        genfix = genfix + str(key) + "=" + str(val) + ';'
    genfix = genfix +  '10=END'
    return genfix

print(neworder())

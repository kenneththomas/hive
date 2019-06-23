import dfix

print('hello')

testmsg = '8=DFIX;11=4a4964c6;49=Tay;56=Spicii;35=D;55=ZVZZT;54=1;38=100;44=10;40=2;10=END'
examplereject = '8=DFIX;35=8;150=8;39=8'

def rejectorder(fixmsg):
    print('received message: {}'.format(fixmsg))
    fixmsg = dfix.parsefix(fixmsg)
    if '37' not in fixmsg.keys():
        print('37 not present, setting 37 to 11')
        fixmsg = dfix.tweak(fixmsg,'37',fixmsg['11'])
    #construct a reject message based on client's message
    rejectmessage = '8=DFIX;150=8;39=8;76=MATU;17=dummy;6=0;14=0;151=0;10=END'
    rejectmessage = dfix.parsefix(rejectmessage)
    #need to pull 54,55,37,11 from client msg
    rejectmessage = dfix.multitweak(rejectmessage,'54={};55={};37={};11={}'.format(fixmsg['54'],fixmsg['55'],fixmsg['37'],fixmsg['11']))
    finalreject = dfix.exportfix(rejectmessage)
    print(finalreject)
    return finalreject


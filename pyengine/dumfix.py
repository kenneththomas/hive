#convert fix message into dictionary for python processing
#TODO - this doesnt like semicolon at the end of the message, need something to handle this
#fix msg
fixmsg='49=Tay;35=D;40=2;38=100;54=1;56=Spicii;8=DUMFIX;55=ZVZZT;11=794752be;44=10'

def parsefix(fixmsg):
    return dict(item.split("=") for item in fixmsg.split(";"))

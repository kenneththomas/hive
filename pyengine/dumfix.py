from collections import OrderedDict as odict


#parse fixmsg into ordered dictionary for python processing
def parsefix(fixmsg):
    return odict(item.split("=") for item in fixmsg.split(";"))


#convert ordered dictionary into fix message
def exportfix(fixdict):
    genfix=''
    for key,val in fixdict.items():
        if key != '10':
            genfix = genfix + str(key) + "=" + str(val) + ';'
        else: # tail tag should not have a semicolon at the end
            genfix = genfix + str(key) + "=" + str(val)
    return genfix

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

#check for certain fix tag value: fix, tag, tag value
def subscription(fixdict,tag,value):
    if fixdict.get(tag) == value:
        return True
    else:
        return False

#change one fix value to another value
def tweak(fixdict,tag,value):
    fixdict.get(tag)
    fixdict.update({tag : value})
    fixdict.get(tag)
    trailer(fixdict) #TODO: only move tag 10 to end if a tag was added by tweak, no reason to do this on every tweak
    return fixdict

#always put tag 10=END at the end
def trailer(fixdict):
    fixdict.move_to_end('10')
    return fixdict
from collections import OrderedDict as odict


#parse fixmsg into ordered dictionary for python processing
def parsefix(fixmsg):
    if fixmsg[-1] == ';':
        fixmsg = fixmsg[:-1]
    return odict(item.split("=") for item in fixmsg.split(";"))


#convert ordered dictionary into fix message
def exportfix(fixdict):
    genfix=''
    #move tag 10 to end
    #if tag 10 exists
    if '10' in fixdict.keys():
        fixdict.move_to_end('10')
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
    addedtag = False # maybe theres a more efficient way to do this
    if tag not in fixdict.keys():
        addedtag = True
    fixdict.update({tag : value})
    if addedtag:
        trailer(fixdict)
    return fixdict

#always put tag 10=END at the end
def trailer(fixdict):
    fixdict.move_to_end('10')
    return fixdict

#remove semicolon if trailer for parsing
def dfixformat(fixmsg):
    if fixmsg[-1] == ";": # check if last character is semicolon
        print('DFIX: Detected DFIX with delimiter trailer, stripping')
        fixmsg = fixmsg[:-1] # strip last character
    return fixmsg

def multitweak(fix,modifyfix):
    modifyfix = parsefix(modifyfix) # parse into dictionary
    for tag in modifyfix:
        newfix = tweak(fix,tag,modifyfix[tag])
    return newfix

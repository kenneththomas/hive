import dumfix
import riskcheck
import marketdata

#accept fixmsg

def fixgateway(fix):
    clientorder = dumfix.parsefix(fix)
    execreport = ordermanager(clientorder)
    #send back to client
    clientexec = dumfix.exportfix(execreport)
    #for now, sending to client simply means printing/returning
    print(clientexec)
    return clientexec

def ordermanager(clientorder):
    #get some tags
    symbol = clientorder.get('55')
    price = clientorder.get('44')
    riskcheck.limitcheck(symbol,int(price))
    execreport = dumfix.tweak(clientorder,'150','8')
    return execreport

import dfix
import riskcheck
import marketdata

#accept fixmsg

def fixgateway(fix):
    clientorder = dfix.parsefix(fix)
    # check for valid values of tag 35
    msgtype = clientorder.get('35')
    if not fixvalidator(valid35, msgtype):
        clientorder = rejectorder(clientorder,msgtype + ' is an invalid value of Tag 35 (MsgType)')
    else:
        clientorder = ordermanager(clientorder)
    #send back to client
    execreport = dfix.tweak(clientorder, '35', '8')
    clientexec = dfix.exportfix(execreport)
    #for now, sending to client simply means printing/returning
    print(clientexec)
    return clientexec

def ordermanager(clientorder):
    #get some tags
    symbol = clientorder.get('55')
    price = clientorder.get('44')
    quantity = clientorder.get('38')
    side = clientorder.get('54')
    #check if symbol exists in MD, reject otherwise
    if not marketdata.marketdataexists(symbol):
        clientorder = rejectorder(clientorder,'market data does not exist for symbol ' + symbol)
    else:
        riskcheckresult = riskcheck.limitcheck(symbol,float(price),int(quantity))
        if riskcheckresult[0] == 'Reject':
            clientorder = rejectorder(clientorder,riskcheckresult[1])
        else:
            #accept order with 150=0
            clientorder = dfix.tweak(clientorder,'150','0')
    return clientorder

def fixvalidator(validlist, value):
    if value in validlist:
        return True
    else:
        return False

#fixvalidator lists
valid35 = ['D']

def rejectorder(rejectedorder,rejectreason):
    print(rejectreason)
    rejectedorder = dfix.tweak(rejectedorder, '150', '8')
    return dfix.tweak(rejectedorder,'58',rejectreason)


def fillsimulate(fsfix):
    #just fill 100 qty if price is "marketable"

    #get relevant tags (symbol, orderqty, price, side)
    symbol = fsfix.get('55')
    orderqty = fsfix.get('38')
    price = fsfix.get('44')
    side = fsfix.get('54')

    #convert price to pennies
    pricepny = int(price) * 1000

    #int values
    intorderqty = int(orderqty)

    marketvalue = (marketdata.getprice(symbol))
    if side == '1': # buy order
        if pricepny > marketvalue:
            if intorderqty <= 100:
                #full fill
                dfix.tweak(fsfix,'150','2')
            elif intorderqty > 100:
                #partial fill
                dfix.tweak(fsfix,'150','1')
    if side == '2': #sell order
        print('not yet.')
    return fsfix



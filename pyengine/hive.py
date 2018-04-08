import dfix
import riskcheck
import marketdata
import mop
import uuid

orderidpool=[] # list that contains used orderids

def fixgateway(fix):
    clientorder = dfix.parsefix(fix)
    # check for valid values of tag 35
    msgtype = clientorder.get('35')
    orderid = clientorder.get('11')
    sendercompid = clientorder.get('49')
    uniqclord = sendercompid + '-' + orderid # used so different clients can use same value of tag 11
    if uniqclord in orderidpool: #reject if duplicate 49 - 11
        clientorder = rejectorder(clientorder,'Duplicate value of tag 11 is not allowed')
        execreport = dfix.tweak(clientorder, '35', '8')
        return dfix.exportfix(execreport)
    else:
        orderidpool.append(uniqclord) # append uniqclord to list
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
        if clientorder.get('40') == '1': # marketorders have no price, but we need a price to limit check
            if price:
                clientorder = rejectorder(clientorder,'Market Orders should not contain price in tag 44')
                return clientorder
            mdprice = float(marketdata.getprice(symbol)) / 100
            riskcheckresult = riskcheck.limitcheck(symbol,mdprice,int(quantity))
        else:
            riskcheckresult = riskcheck.limitcheck(symbol,float(price),int(quantity))
        #riskcheckresult comes back as a list with "Reject" in [0] if the order is rejected
        if riskcheckresult[0] == 'Reject':
            clientorder = rejectorder(clientorder,riskcheckresult[1])
        else:
            if quantity == '100': # for now MOP is only destination
                clientorder = mop.mop(clientorder)
            else: # try to slice order into 100 if qty is not 100, THEN send to MOP from hundoslice
                clientorder = hundoslice(clientorder)
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

def hundoslice(fix): # slices larger order into multiple orders of 100 qty
    moporders=[]
    origqty = int(fix.get('38'))
    sliceable = origqty % 100
    if sliceable == 0: # only slice orders that are divisible by 100
        slicedorderno = int(origqty / 100) # number of orders to slice
        print('Algo: Slicing ' + str(origqty) + ' qty order into ' + str(slicedorderno) + ' slices')
        for i in range (0,slicedorderno):
            newtag11 = 'hs-' + str(uuid.uuid1())[:8]
            slicefix = fix
            slicefix = dfix.tweak(slicefix,'11',newtag11)
            slicefix = dfix.tweak(slicefix,'38','100')
            print(slicefix)
            moporders.append(mop.mop(slicefix))
    else: # reject order if it's not divisible by 100 qty
        fix = rejectorder(fix, 'hundoslice reject: order not divisible by 100')
        return fix
    for order in moporders:
        if order.get('150') != '2':
            filled = False
        else:
            filled = True
    if filled == True: # we need to make this look like the original order
        fix = dfix.tweak(fix, '150', '2')
        fix = dfix.tweak(fix, '38', origqty)  # oriq qty
        fix = dfix.tweak(fix, '14', origqty)  # cum qty
        return fix
    else:
        fix = dfix.tweak(fix, '38', origqty)  # oriq qty
        return fix




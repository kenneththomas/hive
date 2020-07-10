import dfix
import riskcheck
import marketdata
import mop
import uuid
import mutombo

#instance configuration
hostname = 'nyastdev' #not sure if worth implementing something that actually grabs the hostname/ip
instance = 'hive1'
environment = 'dev'

#instance settings
tag11validation = False # determines whether we do duplicate tag 11 validation
defaultcurrency = 'USD' # which currency is used logic for things like risk checking

orderidpool=[] # list that contains used orderids which will be rejected if tag11validation is on
blockedsessions=[] # tag 49 values which will be rejected


def fixgateway(fix):
    clientorder = dfix.parsefix(fix)
    cf = dfix.fix(fix)
    if not fixvalidator(valid35, cf.msgtype):     # check for valid values of tag 35
        clientorder = rejectorder(clientorder,cf.msgtype + ' is an unsupported value of Tag 35 (MsgType)')
        return dfix.exportfix(clientorder)
    if cf.msgtype == 'UAC': #UAC is admin command
        clientorder = adminmgr(clientorder)
        return dfix.exportfix(clientorder)
    #check for blocked client
    if cf.sender in blockedsessions: # blocked sessions
        return dfix.exportfix(rejectorder(clientorder, 'FIX Session blocked'))
    if tag11validation:
        uniqclord = cf.sender + '-' + cf.orderid # used so different clients can use same value of tag 11
        if uniqclord in orderidpool: #reject if duplicate 49 - 11
            clientorder = rejectorder(clientorder,'Duplicate value of tag 11 is not allowed')
            return dfix.exportfix(clientorder)
        else:
            orderidpool.append(uniqclord) # append uniqclord to list
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
    ordertype = clientorder.get('40')
    currency = clientorder.get('15')
    #check if symbol exists in MD, reject otherwise
    if not marketdata.marketdataexists(symbol):
        clientorder = rejectorder(clientorder,'market data does not exist for symbol ' + symbol)
    else:
        if ordertype == '1': # marketorders have no price, but we need a price to limit check
            if price:
                clientorder = rejectorder(clientorder,'Market Orders should not contain price in tag 44')
                return clientorder
            mdprice = float(marketdata.getprice(symbol)) / 100
            riskcheckresult = riskcheck.limitcheck(symbol,mdprice,int(quantity))
        elif ordertype == '2':
            if not price: # limit orders need to have price
            # todo: write test for this and also move this into order type validator function
                clientorder = rejectorder(clientorder,'Limit Orders should contain price in tag 44')
                return clientorder
            if currency: # we assume the default currency if no currency is listed
                if currency != defaultcurrency:
                    print('OM: Detected order with non-default currency')
                    currencyrate = currencyconverter(currency)
                    if currencyrate: #if we have a rate, we convert currency
                        clientorder = dfix.tweak(clientorder, '15', defaultcurrency)
                        newprice = float(price) * currencyrate
                        clientorder = dfix.tweak(clientorder, '44', str(round(newprice,2)))
                    else:
                        clientorder = rejectorder(clientorder,currency + ' Is An Unsupported Currency')
                        return clientorder
            riskcheckresult = riskcheck.limitcheck(symbol,float(price),int(quantity))
        #riskcheckresult comes back as a list with "Reject" in [0] if the order is rejected
        if riskcheckresult[0] == 'Reject':
            clientorder = rejectorder(clientorder,riskcheckresult[1])
        else: # order is all good at this point and can be routed
            clientorder = hiverouter(clientorder)
    return clientorder

def currencyconverter(tag15):
    #conversion values for tag15/USD
    USD = { 'EUR' : 1.20,
            'CAD' : 0.78,
    }
    if tag15 in USD:
        return USD.get(tag15)
    else:
        print('CurrencyConverter: No ' + tag15 + '/' + defaultcurrency + ' rate found')
        return False

validcommands = ['disable fixsession','enable fixsession']

def adminmgr(adminmsg):
    component = adminmsg.get('57')
    command = adminmsg.get('58')
    parameter = adminmsg.get('161')
    if command in validcommands:
        print('AdminMgr: Detected Admin Command')
        if command == 'disable fixsession':
            blockedsessions.append(parameter)
            uar = dfix.tweak(adminmsg, '58', parameter + ' has been disabled')
        elif command == 'enable fixsession':
            blockedsessions.remove(parameter)
            uar = dfix.tweak(adminmsg,'58', parameter + ' has been unblocked')
    else: # reject invalid admin command
        uar = dfix.tweak(adminmsg, '58', 'Invalid Admin Command')
    uar = dfix.tweak(uar,'35','UAR')
    return uar

def hiverouter(fix):
    quantity = fix.get('38')
    ordertype = fix.get('40')
    if '57' not in fix.keys():
        fix['57'] = 'unknown'
    if fix['57'] == 'MATU':
        result = mutombo.rejectorder(dfix.exportfix(fix))
        return dfix.parsefix(result)
    elif ordertype == '1': # market order destinations
        if quantity == '100': # order quantity 100 doesn't need to be sliced
            outboundfix = mop.mop(fix)
        else: # try to slice
            outboundfix = hundoslice(fix)
        return outboundfix
    else:
        noroute = rejectorder(fix, 'no route found for order')
        return noroute

def fixvalidator(validlist, value):
    if value in validlist:
        return True
    else:
        return False

#fixvalidator lists
valid35 = ['D','UAC']

def rejectorder(rejectedorder,rejectreason):
    print(rejectreason)
    rejectedorder = dfix.multitweak(rejectedorder,'35=8;150=8')
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
        fix = dfix.tweak(fix, '38', origqty)  # orig qty
        fix = dfix.tweak(fix, '14', origqty)  # cum qty
        return fix
    else:
        fix = dfix.tweak(fix, '38', origqty)  # orig qty
        return fix

def quoter(fix):
    mdrequesttype = fix.get('263')
    norelatedsymbols = fix.get('146')
    symbol = fix.get('55')
    if mdrequesttype != 1:
        response = rejectorder(fix, 'only snapshot (263=1) currently supported')
        return response
    if norelatedsymbols > 1:
        response = rejectorder(fix, 'only one symbol allowed for market data requests')
        return response
    return response
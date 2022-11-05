import sys
import dfix
import uuid
import datetime
sys.path.insert(1, 'tests/resources')
import devresources as devr

#dev resources, normally this would be in config or database
clients = devr.clients
entity = devr.entity
accounts = devr.accounts
defaultaccounts = devr.defaultaccounts

def parse_new_msg(fixmsg):

    try:
        pfix = dfix.parsefix(fixmsg)
    except ValueError:
        print('could not parse fix message')
        return False
    
    outgoing_fix = dfix.exportfix(on_new_msg(pfix))

    print('outgoing fix:')
    print(outgoing_fix)

    return outgoing_fix

def on_new_msg(pfix):

    print('on_new_msg() received new msg: {}'.format(pfix))

    # get some basic fixtags
    sendercompid = pfix['49']
    targetcompid = pfix['56']
    msgtype = pfix['35']

    # client validation
    client_validation_result = client_validation(sendercompid,targetcompid)
    if client_validation_result[0] == False:
        response = reject_order(pfix, client_validation_result[1])
        return response

    if msgtype == 'D':
        print('on_new_msg() msg is a new order')
        response = on_new_order(pfix)

    return response


def client_validation(sendercompid,targetcompid):
    if sendercompid not in clients.keys():
        print(f'client {sendercompid} not found in client list')
        return [False,f'sendercompid "{sendercompid}" unknown']
    if targetcompid != clients[sendercompid]:
        print(f'client {sendercompid} targetcompid {targetcompid} does not match')
        return [False,f'targetcompid "{targetcompid}" unknown']
    else:
        return [True]

def reject_order(fixmsg, reason):
    print(f'reject_order() reason: {reason}')
    fixmsg = execreport_builder(fixmsg)
    #set reject reason
    fixmsg['58'] = reason

    #set reject exectype
    fixmsg['39'] = '8'
    fixmsg['150'] = '8'
    print('reject_order() reject fixmsg: {}'.format(fixmsg))
    return fixmsg

def execreport_builder(fixmsg):
    #flip compids
    sendercompid = fixmsg['49']
    targetcompid = fixmsg['56']
    fixmsg['49'] = targetcompid
    fixmsg['56'] = sendercompid
    #set tag 17 to 10 digit uuid
    fixmsg['17'] = str(uuid.uuid4())[:10]
    #if no tag 37 is set, set to 10 digit uuid
    if '37' not in fixmsg.keys():
        fixmsg['37'] = str(uuid.uuid4())[:10]
    #set tag 35 to 8
    fixmsg['35'] = '8'
    #set timestamp
    fixmsg['52'] = datetime.datetime.now().strftime('%Y%m%d-%H:%M:%S.%f')[:-3]
    return fixmsg

def on_new_order(fixmsg):

    fixmsg = client_manager(fixmsg)

    return fixmsg


def client_manager(fixmsg):
    sendercompid =  fixmsg['49']
    try:
        clientid = fixmsg['109']
    except KeyError:
        print('ClientID missing, will attempt to derive from sendercompid-entity mapping - client_manager()')
        fixmsg['109'] = entity[sendercompid]
        clientid = fixmsg['109']
        print(f'ClientID {clientid} found for {sendercompid}! - client_manager()')
    if '1' not in fixmsg.keys():
        #if no account is set, set to default account
        try:
            fixmsg['1'] = defaultaccounts[fixmsg['109']]
            account = fixmsg['1']
            print(f'Using default account {account} for {clientid} - client_manager()')
        except KeyError:
            try:
                account = fixmsg['1']
            except KeyError:
                account = 'guest'
    else:
        account = fixmsg['1']
    
    #account validation
    validaccounts = accounts[clientid]
    if account not in validaccounts:
        fixmsg = reject_order(fixmsg, f'account "{account}" not found for client "{clientid}"')

    return fixmsg

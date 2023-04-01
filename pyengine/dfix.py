from collections import OrderedDict as odict
import datetime
import uuid


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

class execreport_gen:
    def create_cancel_execution_report(order):
        exec_report = odict()
        exec_report['8'] = 'FIX.4.2'
        exec_report['35'] = '8'
        exec_report['49'] = 'BARI'
        exec_report['11'] = order.orderid
        exec_report['37'] = order.orderid  # Assuming order ID is the same as the order's unique identifier
        exec_report['39'] = '4'  # Canceled order status
        exec_report['54'] = order.side
        exec_report['55'] = order.symbol
        exec_report['150'] = '4'  # Canceled exec type
        exec_report['60'] = datetime.datetime.now().strftime('%Y%m%d-%H:%M:%S')  # Transaction time
        print(exportfix(exec_report))

        return exec_report
    
    def generate_unfilled_ioc_execution_report(order):
        report = odict()
        report['8'] = 'FIX.4.2'
        report['35'] = '8'
        report['49'] = 'BARI'
        report['11'] = order.orderid
        report['17'] = str(uuid.uuid4())[:10]
        report['37'] = order.orderid  # Order ID
        report['39'] = '4'  # Canceled order status
        report['54'] = order.side
        report['55'] = order.symbol
        report['150'] = '4'  # Canceled exec type
        report['14'] = order.original_qty - order.qty  # Cumulative quantity executed
        report['32'] = 0  # Quantity executed for this report
        report['31'] = 0
        report['6'] = 0
        report['151'] = order.qty  # Leaves quantity
        report['60'] = datetime.datetime.now().strftime('%Y%m%d-%H:%M:%S.%f')[:-3]
        report['52'] = report['60']
        report['30'] = 'BARI'
        report['76'] = 'BARI'

        print(exportfix(report))
        return report

    def generate_new_order_execution_report(order):
        report = odict()
        report['8'] = 'FIX.4.2'
        report['35'] = '8'
        report['49'] = 'BARI'
        report['11'] = order.orderid
        report['17'] = str(uuid.uuid4())[:10]
        report['37'] = order.orderid  # Order ID
        report['39'] = '0'  # New order status
        report['54'] = order.side
        report['55'] = order.symbol
        report['150'] = '0'  # New order execution type
        report['14'] = 0  # Cumulative quantity executed
        report['32'] = 0  # Quantity executed for this report (LastShares)
        report['151'] = order.qty  # LeavesQty (remaining quantity)
        report['60'] = datetime.datetime.now().strftime('%Y%m%d-%H:%M:%S.%f')[:-3]
        report['52'] = report['60']
        report['30'] = 'BARI'
        report['76'] = 'BARI'
        print(exportfix(report))
        return report
    
    def generate_reject_execution_report(order, reject_reason):
        report = odict()
        report['8'] = 'FIX.4.2'
        report['35'] = '8'
        report['49'] = 'BARI'
        report['11'] = order.orderid
        report['17'] = str(uuid.uuid4())[:10]
        report['37'] = order.orderid  # Order ID
        report['39'] = '8'  # Rejected order status
        report['54'] = order.side
        report['55'] = order.symbol
        report['150'] = '8'  # Rejected execution type
        report['14'] = 0  # Cumulative quantity executed
        report['32'] = 0  # Quantity executed for this report (LastShares)
        report['151'] = order.qty  # LeavesQty (remaining quantity)
        report['60'] = datetime.datetime.now().strftime('%Y%m%d-%H:%M:%S.%f')[:-3]
        report['52'] = report['60']
        report['58'] = reject_reason  # Reject reason
        print(exportfix(report))
        return report
    
    def generate_execution_report(order, matched_qty, status,last_px=0):
        report = odict()
        report['8'] = 'FIX.4.2'
        report['35'] = '8'
        report['49'] = 'BARI'
        report['56'] = order.sendercompid
        report['11'] = order.orderid
        report['17'] = str(uuid.uuid4())[:10]
        report['37'] = order.orderid  # Order ID
        report['39'] = status  # Order status: '2' for fully executed, '1' for partially executed
        report['54'] = order.side
        report['55'] = order.symbol
        report['150'] = '2' if status == '2' else '1'  # Execution type: '2' for trade, '1' for partial fill
        report['14'] = order.original_qty - order.qty  # Cumulative quantity executed
        report['32'] = matched_qty  # Quantity executed for this report (LastShares)
        report['151'] = order.qty  # LeavesQty (remaining quantity)
        report['31'] = last_px
        report['6'] = order.limitprice  # Average execution price
        report['60'] = datetime.datetime.now().strftime('%Y%m%d-%H:%M:%S.%f')[:-3]
        report['52'] = report['60']
        report['30'] = 'BARI'
        report['76'] = 'BARI'

        #also print as fix
        print(exportfix(report))
        
        return report  # Return the report
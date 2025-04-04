import dfix
from collections import OrderedDict
import uuid
import datetime
from tabulate import tabulate

bookshelf = {}  # contains books of all symbols
fillcontainer = {}  # contains all fills
orderid_container = {} # contains orderids to prevent duplicate orderids


class BariOrder:
    def __init__(self, fix):

        self.shouldreject = False
        #mandatory parameters
        self.orderid = fix['11']
        self.side = fix['54']
        self.symbol = fix['55']
        try:
            self.qty = int(fix['38'])
        except ValueError:
            self.shouldreject = True
            self.rejectreason = 'Invalid quantity'
            self.qty = float(fix['38'])
        self.orderstatus = '0'
        self.sendercompid = fix['49']



        #assume day order if not set
        self.timeinforce = fix['59'] if '59' in fix else '0'
        #assume limit order if not set
        self.ordertype = fix['40'] if '40' in fix else '2'
        #assume USD if not set
        self.currency = fix['15'] if '15' in fix else 'USD'

        #if limit order, need limit price
        if self.ordertype == '2':
            try:
                self.limitprice = float(fix['44'])
            except ValueError:
                self.shouldreject = True
                self.rejectreason = 'Invalid limit price'
        elif self.ordertype == '1':
            self.limitprice = 'MKT'

        #status
        self.is_canceled = False
        self.is_rejected = False
        try:
            self.original_qty = int(fix['38']) # used for calculating the executed quantity
        except ValueError:
            self.shouldreject = True
            self.rejectreason = 'Invalid quantity'

        #change to lastpx (tag 31) if order gets executed
        self.lastpx = False


def matcher(buyer, seller, potential_lastpx):
    # Prevent self-match
    if buyer.sendercompid == seller.sendercompid:
        print('Self-match prevented! - buyer:', buyer.sendercompid, 'seller:', seller.sendercompid, 'symbol:', buyer.symbol, 'qty:')
        return 0

    if buyer.limitprice < seller.limitprice:
        return 0
    else:
        matched_qty = min(buyer.qty, seller.qty)
        buyer.qty -= matched_qty
        seller.qty -= matched_qty

        buyer_status = '2' if buyer.qty == 0 else '1'
        seller_status = '2' if seller.qty == 0 else '1'

        # Calculate fill price based on passive (resting) order's limit price
        fill_price = potential_lastpx

        buyer_execution_report = dfix.execreport_gen.generate_execution_report(buyer, matched_qty, buyer_status, fill_price)
        seller_execution_report = dfix.execreport_gen.generate_execution_report(seller, matched_qty, seller_status, fill_price)

        # Send execution reports to buyer and seller
        print("Buyer Execution Report:", buyer_execution_report)
        print("Seller Execution Report:", seller_execution_report)
        
        # Use a composite key that includes both order ID and a timestamp to ensure uniqueness
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
        fillcontainer[f"{buyer.orderid}_{timestamp}"] = buyer_execution_report
        fillcontainer[f"{seller.orderid}_{timestamp}"] = seller_execution_report

        return matched_qty


def evaluate_book(new_order, book):
    potential_matches = [
        order for order in book
        if order.side != new_order.side and not order.is_canceled
    ]

    matched_qty = 0

    # Sort potential matches by price (best price first)
    if new_order.side == '1':  # Buy order
        # For buy orders, match against sell orders with lowest prices first
        potential_matches.sort(key=lambda order: order.limitprice)
    else:  # Sell order
        # For sell orders, match against buy orders with highest prices first
        potential_matches.sort(key=lambda order: order.limitprice, reverse=True)

    for potential_match in potential_matches:
        # potential fill price is the passive (resting) order's limit price
        potential_lastpx = potential_match.limitprice
        fill_qty = matcher(new_order, potential_match, potential_lastpx) if new_order.side == '1' else matcher(potential_match, new_order, potential_lastpx)

        if fill_qty > 0:
            new_order.lastpx = potential_lastpx
            potential_match.lastpx = potential_lastpx
            matched_qty += fill_qty
            if potential_match.qty == 0:
                book.remove(potential_match)
            if new_order.qty == 0:
                break

    if new_order.qty > 0:
        if new_order.timeinforce != '3':
            book.append(new_order)
        else:
            print(f"Immediate or Cancel order {new_order.orderid} not fully executed. Remaining quantity: {new_order.qty}")
            unfilled_ioc_exec_report = dfix.execreport_gen.generate_unfilled_ioc_execution_report(new_order)
            print("Unfilled IOC Execution Report:", unfilled_ioc_exec_report)
        bookshelf[new_order.symbol] = book

def side_to_str(side):
    return 'Buy' if side == '1' else 'Sell'

def on_new_order(new_order):
    print(f'Received Order: {new_order}')
    parsed_fix = dfix.parsefix(new_order)
    new_order = BariOrder(parsed_fix)

    # Duplicate Order Validation with key as tag 49 and tag 11 combined
    if new_order.sendercompid + new_order.orderid in orderid_container.keys():
        rejectreport = reject_order(new_order, f'Duplicate Order Reject - {new_order.sendercompid} {new_order.orderid}')
        return dfix.exportfix(rejectreport)
    else:
        orderid_container[new_order.sendercompid + new_order.orderid] = new_order

    # Reject market order if not IOC
    if new_order.ordertype == '1' and new_order.timeinforce != '3':
        rejectreport = reject_order(new_order, 'Market orders must be immediate or cancel')
        return dfix.exportfix(rejectreport)

    if new_order.ordertype == '1':
        # Set limit price based on the best available price in the bookshelf
        if new_order.symbol in bookshelf and bookshelf[new_order.symbol]:  # Check if list is not empty
            opposite_side_orders = [order for order in bookshelf[new_order.symbol] 
                                   if order.side != new_order.side and not order.is_canceled]
            if opposite_side_orders:
                if new_order.side == '1':  # Buy order
                    best_price = min([order.limitprice for order in opposite_side_orders])
                else:  # Sell order
                    best_price = max([order.limitprice for order in opposite_side_orders])
                new_order.limitprice = best_price
            else:
                # No opposite side orders available
                rejectreport = dfix.execreport_gen.generate_unfilled_ioc_execution_report(new_order)
                return dfix.exportfix(rejectreport)
        else:
            # Reject like an IOC if symbol not in bookshelf or empty
            rejectreport = dfix.execreport_gen.generate_unfilled_ioc_execution_report(new_order)
            return dfix.exportfix(rejectreport)
    
    # side validation
    if new_order.side not in ['1', '2']:
        if new_order.side == '5':
            rejectreport = reject_order(new_order, 'Please send short sell orders as sell orders.')
            return dfix.exportfix(rejectreport)
        rejectreport = reject_order(new_order, f'Invalid side - {new_order.side}')
        return dfix.exportfix(rejectreport)

    # parsing error rejects
    if new_order.shouldreject:
        rejectreport = reject_order(new_order, new_order.rejectreason)
        return dfix.exportfix(rejectreport)

    #reject if not limit or market order
    if new_order.ordertype not in ['1', '2']:
        rejectreport = reject_order(new_order, 'Only limit and market orders are supported')
        return dfix.exportfix(rejectreport)
    
    # reject if futures or options using tag 167 FUT or OPT
    if '167' in parsed_fix:
        rejectreport = reject_order(new_order, 'Futures and options are not supported')
        return dfix.exportfix(rejectreport)
    
    #reject if negative quantity
    if new_order.qty < 0:
        rejectreport = reject_order(new_order, f'are u kidding me? ur telling me u want to {side_to_str(new_order.side)} {new_order.qty} shares of {new_order.symbol}?')
        return dfix.exportfix(rejectreport)
    
    #reject if fractional quantity - on 3/31/2023 this code cant actually be hit because the fix parser expects int and it will reject earlier.
    if new_order.qty % 1 != 0:
        rejectreport = reject_order(new_order, f'Invalid QTY: {new_order.qty} - fractional shares are not supported')
        return dfix.exportfix(rejectreport)
    
    #reject if negative price
    if new_order.limitprice < 0:
        rejectreport = reject_order(new_order, f'((({new_order.sendercompid}))) - REEEEEEEJECTED - negative price: {new_order.limitprice} is not supported')
        return dfix.exportfix(rejectreport)
    
    #reject if not 15=USD
    if new_order.currency != 'USD':
        if new_order.currency in slurs:  # Fixed dict access
            rejectreport = reject_order(new_order, f'CurrencyValidationReject: {slurs[new_order.currency]} - we dont take {new_order.currency} round here')
            return dfix.exportfix(rejectreport)  # Added missing return
        rejectreport = reject_order(new_order, f'MURRRRRKAH - we dont take {new_order.currency} round here')
        return dfix.exportfix(rejectreport)
    
    new_order_execution_report = dfix.execreport_gen.generate_new_order_execution_report(new_order)
    print("New Order Execution Report:", new_order_execution_report)

    # Add the new order execution report to the fillcontainer with a composite key
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
    fillcontainer[f"{new_order.orderid}_{timestamp}_new"] = new_order_execution_report

    if new_order.symbol not in bookshelf.keys():
        bookshelf[new_order.symbol] = [new_order]
        if new_order.timeinforce == '3':
            bookshelf[new_order.symbol] = []
            print(f"Immediate or Cancel order {new_order.orderid} not fully executed. Remaining quantity: {new_order.qty}")
            unfilled_ioc_exec_report = dfix.execreport_gen.generate_unfilled_ioc_execution_report(new_order)
            print("Unfilled IOC Execution Report:", unfilled_ioc_exec_report)
    else:
        #display_book(bookshelf[new_order.symbol])
        evaluate_book(new_order, bookshelf[new_order.symbol])

    # return exported new order execution report
    return dfix.exportfix(new_order_execution_report)


def display_book(book):
    try:
        print('Order Book: ', book[0].symbol, 'at', datetime.datetime.now().strftime('%Y%m%d-%H:%M:%S.%f')[:-3])
    except IndexError:
        print('Order Book is empty.')

    buys = [order for order in book if order.side == '1']
    sells = [order for order in book if order.side == '2']

    max_rows = max(len(buys), len(sells))
    combined_data = []

    for i in range(max_rows):
        row = []
        if i < len(buys):
            buy_order = buys[i]
            row.extend([buy_order.orderid, buy_order.sendercompid, buy_order.original_qty, buy_order.qty, buy_order.limitprice])
        else:
            row.extend(['', '', '', '', ''])

        if i < len(sells):
            sell_order = sells[i]
            row.extend([sell_order.limitprice, sell_order.qty, sell_order.original_qty, sell_order.sendercompid, sell_order.orderid])
        else:
            row.extend(['', '', '', '', ''])

        combined_data.append(row)

    headers = [
        'Bid Order ID', 'Bid SenderCompID', 'Bid Original Qty', 'Bid Remaining Qty', 'Bid Price',
        'Ask Price', 'Ask Remaining Qty', 'Ask Original Qty', 'Ask SenderCompID', 'Ask Order ID'
    ]

    print('Combined Order Book:')
    print(tabulate(combined_data, headers=headers, tablefmt='grid'))

def on_cancel_order(order_id):
    for symbol, book in bookshelf.items():
        for order in book:
            if order.orderid == order_id:
                order.is_canceled = True
                print(f"Order {order_id} has been canceled.")
                cancel_exec_report = dfix.execreport_gen.create_cancel_execution_report(order)
                print(f"Cancellation Execution Report: {cancel_exec_report}")
                
                # Add the cancellation to the fillcontainer with a composite key
                timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
                fillcontainer[f"{order_id}_{timestamp}_cancel"] = cancel_exec_report
                
                return
    print(f"Order {order_id} not found in the order book.")

#TODO - actually use this function
def remove_canceled_orders():
    for symbol, book in bookshelf.items():
        bookshelf[symbol] = [order for order in book if not order.is_canceled]

def reject_order(order, reject_reason):
    reject_execution_report = dfix.execreport_gen.generate_reject_execution_report(order, reject_reason)
    print("Reject Execution Report:", reject_execution_report)
    
    # Add the rejection to the fillcontainer with a composite key
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
    fillcontainer[f"{order.orderid}_{timestamp}_reject"] = reject_execution_report
    
    return reject_execution_report


#currency rejection reasons
slurs = {

        'BTC' : 'buy the dip, short the VIX, FUCK BITCOIN'
}
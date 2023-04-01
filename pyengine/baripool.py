import dfix
from collections import OrderedDict
import uuid
import datetime
from tabulate import tabulate

bookshelf = {}  # contains books of all symbols


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
        self.limitprice = float(fix['44'])
        self.orderstatus = '0'
        self.sendercompid = fix['49']


        #optional parameters
        #assume day order if not set
        self.timeinforce = fix['59'] if '59' in fix else '0'
        #assume limit order if not set
        self.ordertype = fix['40'] if '40' in fix else '2'
        #assume USD if not set
        self.currency = fix['15'] if '15' in fix else 'USD'

        #status
        self.is_canceled = False
        self.is_rejected = False
        try:
            self.original_qty = int(fix['38']) # used for calculating the executed quantity
        except ValueError:
            self.shouldreject = True
            self.rejectreason = 'Invalid quantity'




def matcher(buyer, seller):
    # Prevent self-match
    if buyer.sendercompid == seller.sendercompid:
        print('Self-match prevented! - buyer:', buyer.sendercompid, 'seller:', seller.sendercompid, 'symbol:', buyer.symbol, 'qty:', )
        return 0

    if buyer.limitprice < seller.limitprice:
        return 0
    else:
        matched_qty = min(buyer.qty, seller.qty)
        buyer.qty -= matched_qty
        seller.qty -= matched_qty

        buyer_status = '2' if buyer.qty == 0 else '1'
        seller_status = '2' if seller.qty == 0 else '1'

        buyer_execution_report = dfix.execreport_gen.generate_execution_report(buyer, matched_qty, buyer_status)
        seller_execution_report = dfix.execreport_gen.generate_execution_report(seller, matched_qty, seller_status)

        # Send execution reports to buyer and seller
        print("Buyer Execution Report:", buyer_execution_report)
        print("Seller Execution Report:", seller_execution_report)

        return matched_qty


def evaluate_book(new_order, book):
    potential_matches = [
        order for order in book
        if order.side != new_order.side and not order.is_canceled
    ]

    matched_qty = 0

    for potential_match in potential_matches:
        fill_qty = matcher(new_order, potential_match) if new_order.side == '1' else matcher(potential_match, new_order)

        if fill_qty > 0:
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

    # validations

    # side validation
    if new_order.side not in ['1', '2']:
        if new_order.side == '5':
            rejectreport = reject_order(new_order, 'Please send short sell orders as sell orders.')
            return
        rejectreport = reject_order(new_order, f'Invalid side - {new_order.side}')
        return dfix.exportfix(rejectreport)

    # parsing error rejects
    if new_order.shouldreject:
        rejectreport = reject_order(new_order, new_order.rejectreason)
        return dfix.exportfix(rejectreport)

    #reject if not limit order
    if new_order.ordertype != '2':
        rejectreport = reject_order(new_order, 'Only limit orders are supported')
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
        if new_order.currency in slurs.keys():
            rejectreport = reject_order(new_order, f'CurrencyValidationReject: {slurs[new_order.currency]} - we dont take {new_order.currency} round here')
        rejectreport = reject_order(new_order, f'MURRRRRKAH - we dont take {new_order.currency} round here')
        return dfix.exportfix(rejectreport)
    

    
    

    new_order_execution_report = dfix.execreport_gen.generate_new_order_execution_report(new_order)
    print("New Order Execution Report:", new_order_execution_report)

    if new_order.symbol not in bookshelf.keys():
        bookshelf[new_order.symbol] = [new_order]
        if new_order.timeinforce == '3':
            bookshelf[new_order.symbol] = []
            print(f"Immediate or Cancel order {new_order.orderid} not fully executed. Remaining quantity: {new_order.qty}")
            unfilled_ioc_exec_report = dfix.execreport_gen.generate_unfilled_ioc_execution_report(new_order)
            print("Unfilled IOC Execution Report:", unfilled_ioc_exec_report)
    else:
        display_book(bookshelf[new_order.symbol])
        evaluate_book(new_order, bookshelf[new_order.symbol])

    # return exported new order execution report
    return dfix.exportfix(new_order_execution_report)


def display_book_legacy(book):
    # prints buys and sells separately instead of together
    try:
        print('Order Book: ', book[0].symbol, 'at', datetime.datetime.now().strftime('%Y%m%d-%H:%M:%S.%f')[:-3])
    except IndexError:
        print('Order Book is empty.')

    buys = [order for order in book if order.side == '1']
    sells = [order for order in book if order.side == '2']

    buys_data = [[order.orderid, order.original_qty, order.qty, order.limitprice, order.sendercompid] for order in buys]
    sells_data = [[order.orderid, order.original_qty, order.qty, order.limitprice, order.sendercompid] for order in sells]

    headers = ['Order ID', 'Original Quantity', 'Remaining Quantity', 'Price', 'SenderCompID']

    print('Buys:')
    print(tabulate(buys_data, headers=headers, tablefmt='grid'))
    print('Sells:')
    print(tabulate(sells_data, headers=headers, tablefmt='grid'))

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
                return
    print(f"Order {order_id} not found in the order book.")

#TODO - actually use this function
def remove_canceled_orders():
    for symbol, book in bookshelf.items():
        bookshelf[symbol] = [order for order in book if not order.is_canceled]





def reject_order(order, reject_reason):
    reject_execution_report = dfix.execreport_gen.generate_reject_execution_report(order, reject_reason)
    print("Reject Execution Report:", reject_execution_report)
    return reject_execution_report


#currency rejection reasons
slurs = {
        'GBP': 'no tea no shade',
        'EUR': 'MURRRRRKAH!!',
        'CAD': 'canadian money is literally just monopoly money',
        'JPY': 'lets eat this raw fish even though we have the means to cook it',
        'AUD' : 'im in australia. oh noirrr.',
        'NZD' : 'get out of here with your lord of the rings money',
        'FRF' : 'hon hon hon, that is not a thing anymore',
        'HKD' : 'what is this, a chinese currency for ants?',
        'CHF' : 'this is probably fraud and we dont have a legal department',
        'SGD' : 'can is can lah, cannot cannot.',
        'RUB' : 'i dont want to go to jail so i cannot accept this',
        'MXN' : 'taco bell is not a currency',
        'SEK' : 'i dont know what this is but it sounds like a disease',
        'CNY' : 'china #1 but',
        'TWD' : 'taiwan is part of china',
        'KRW' : 'what, did you win squid game?',
        'BRL' : 'huehuehue come to brazil!',
        'INR' : 'slow down ganondorf',
        'ZAR' : 'why don\'t you just go and invest in a vuvuzela factory instead?',
        'SAR' : 'just send me some oil instead',
        'ITL' : 'italian boomer money',
        'BTC' : 'buy the dip, short the VIX, FUCK BITCOIN'
}
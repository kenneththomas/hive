import dfix
from collections import OrderedDict
import uuid
import datetime
from tabulate import tabulate

bookshelf = {}  # contains books of all symbols


class BariOrder:
    def __init__(self, fix):
        self.orderid = fix['11']
        self.side = fix['54']
        self.symbol = fix['55']
        self.qty = int(fix['38'])
        self.limitprice = float(fix['44'])
        self.orderstatus = '0'
        self.is_canceled = False


def generate_execution_report(order, matched_qty, status):
    report = OrderedDict()
    report['11'] = order.orderid
    report['17'] = str(uuid.uuid4())[:10]
    report['37'] = order.orderid  # Order ID
    report['39'] = status  # Order status: '2' for fully executed, '1' for partially executed
    report['54'] = order.side
    report['55'] = order.symbol
    report['150'] = '2' if status == '2' else '1'  # Execution type: '2' for trade, '1' for partial fill
    report['14'] = matched_qty  # Cumulative quantity executed
    report['32'] = matched_qty  # Quantity executed for this report
    report['31'] = order.limitprice  # Execution price
    report['6'] = order.limitprice  # Average execution price
    report['60'] = datetime.datetime.now().strftime('%Y%m%d-%H:%M:%S.%f')[:-3]
    report['52'] = report['60']
    report['30'] = 'BARI'
    report['76'] = 'BARI'
    return report

def matcher(buyer, seller):
    if buyer.limitprice < seller.limitprice:
        return 0
    else:
        matched_qty = min(buyer.qty, seller.qty)
        buyer.qty -= matched_qty
        seller.qty -= matched_qty

        buyer_status = '2' if buyer.qty == 0 else '1'
        seller_status = '2' if seller.qty == 0 else '1'

        buyer_execution_report = generate_execution_report(buyer, matched_qty, buyer_status)
        seller_execution_report = generate_execution_report(seller, matched_qty, seller_status)

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
        book.append(new_order)
        bookshelf[new_order.symbol] = book


def on_new_order(new_order):
    parsed_fix = dfix.parsefix(new_order)
    new_order = BariOrder(parsed_fix)

    if new_order.symbol not in bookshelf.keys():
        bookshelf[new_order.symbol] = [new_order]
    else:
        display_book(bookshelf[new_order.symbol])
        evaluate_book(new_order, bookshelf[new_order.symbol])


def display_book(book):
    buys = [order for order in book if order.side == '1']
    sells = [order for order in book if order.side == '2']

    buys_data = [[order.orderid, order.qty, order.limitprice] for order in buys]
    sells_data = [[order.orderid, order.qty, order.limitprice] for order in sells]

    headers = ['Order ID', 'Quantity', 'Price']

    print('Buys:')
    print(tabulate(buys_data, headers=headers, tablefmt='grid'))
    print('Sells:')
    print(tabulate(sells_data, headers=headers, tablefmt='grid'))

def on_cancel_order(order_id):
    for symbol, book in bookshelf.items():
        for order in book:
            if order.orderid == order_id:
                order.is_canceled = True
                print(f"Order {order_id} has been canceled.")
                cancel_exec_report = create_cancel_execution_report(order)
                print(f"Cancellation Execution Report: {cancel_exec_report}")
                return
    print(f"Order {order_id} not found in the order book.")

#TODO - actually use this function
def remove_canceled_orders():
    for symbol, book in bookshelf.items():
        bookshelf[symbol] = [order for order in book if not order.is_canceled]

def create_cancel_execution_report(order):
    exec_report = OrderedDict()
    exec_report['11'] = order.orderid
    exec_report['37'] = order.orderid  # Assuming order ID is the same as the order's unique identifier
    exec_report['39'] = '4'  # Canceled order status
    exec_report['54'] = order.side
    exec_report['55'] = order.symbol
    exec_report['150'] = '4'  # Canceled exec type
    exec_report['60'] = datetime.datetime.now().strftime('%Y%m%d-%H:%M:%S')  # Transaction time

    return exec_report
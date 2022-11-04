from tkinter.simpledialog import SimpleDialog
import dfix

bookshelf = {} # contains books of all symbols

class bari_order():
    def __init__(self, fix):
        self.orderid = fix['11']
        self.side = fix['54']
        self.symbol = fix['55']
        self.qty = fix['38']
        self.limitprice = float(fix['44'])
        self.orderstatus = '0'

def matcher(buyer,seller):
    # returns quantity matched, 0 if no match

    if buyer.limitprice < seller.limitprice:
        print('matcher() buyer price: {} seller price {} - NO MATCH'.format(buyer.limitprice,seller.limitprice))
        return 0
    else:
        print('matcher() buyer price: {} seller price {} - MATCH!'.format(buyer.limitprice,seller.limitprice))

        # currently only supports full quantity match
        if buyer.qty != seller.qty:
            print('matcher() partial matching currently not supported')
            return 0

        return int(buyer.qty)
    
def evaluate_book(neworder,book):
    ordercount = len(book)
    print('evaluate_book() {} orders resting'.format(ordercount))

    display_book(book)

    potential_matches = []
    if neworder.side == '1':
        for order in book:
            if order.side == '2':
                potential_matches.append(order)
    elif neworder.side == '2':
        for order in book:
            if order.side == '1':
                potential_matches.append(order)

    cumqty = 0

    for pm in potential_matches:
        if neworder.side == '1':
            fillqty = matcher(neworder,pm)
        elif neworder.side == '2':
            fillqty = matcher(pm,neworder)
        
        if fillqty > 0:
            print('evaluate_book() found fill so no longer evaluating')
            cumqty += fillqty
            #remove match from book
            book.remove(pm)
            break

    if cumqty == 0:
        bookshelf[neworder.symbol].append(neworder)
    
def on_new_order(neworder):
    print('on_new_order() received new order: {}'.format(neworder))
    pf = dfix.parsefix(neworder)
    neworder = bari_order(pf)

    if neworder.symbol not in bookshelf.keys():
        print('on_new_order() new symbol, creating new book')
        bookshelf[neworder.symbol] = [neworder]
    else:
        evaluate_book(neworder,bookshelf[neworder.symbol])

def display_book(book):
    print('display_book() - displaying book')
    buys = []
    sells = []
    
    for order in book:
        if order.side == '1':
            buys.append(order)
        elif order.side == '2':
            sells.append(order)

    print('display_book() - buys')
    for order in buys:
        print('qty: {} price: {}'.format(order.qty,order.limitprice))
    print('display_book() - sells')
    for order in sells:
        print('qty: {} price: {}'.format(order.qty,order.limitprice))
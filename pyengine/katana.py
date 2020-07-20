def compareprice(side, p1, p2):
    if side == 'buy':
        if p1 <= p2:
            return True
        else:
            return False
    elif side == 'sell':
        if p1 >= p2:
            return True
        else:
            return False


def matcher(side,qty,book):

    slices = []
    unusedquotes = ''

    print(book)
    print(qty)

    while qty > 0:

        # if there's no quotes, we return whatever we got beforehand
        if len(book.keys()) == 0:
            print('no quotes left')
            return slices

        # all of these variables should be replaced by the best possible option
        bestprice = 'none'
        bestid = 'none'

        for quote in book.keys():
            price = book[quote][0]
            qqty = book[quote][1]

            # the first quote is inherently the best price as there is nothing to compare to
            if bestprice == 'none':
                bestprice = price

            if compareprice(side,price,bestprice):

                # log quotes that were evaluated but not chosen on a single line
                if len(unusedquotes) > 0:
                    print('following quotes were evaluated but not selected for this round: {}'.format(unusedquotes))
                    unusedquotes = ''

                print('selected best quote:{}:{}'.format(quote,price))
                bestprice = price
                bestid = quote
                bqqty = book[quote][1]
                bexch = book[quote][2]

                ordqty = bqqty # in a normal case we use the full quote
                if bqqty > qty: # if we dont need the whole thing, we just use what we actually need
                    print('quote is larger than needed {}, will only use needed qty from available {}'.format(qty,bqqty))
                    ordqty = qty
            else:
                unusedquotes = '{} {} ({} @ {}),'.format(unusedquotes,quote,qqty,price)

        exslice = '35=D;40=2;54=1;11={};38={};44={};57={};'.format(bestid,ordqty,bestprice,bexch)
        print(exslice)
        slices.append(exslice)

        oldqty = qty
        qty = qty - bqqty
        print('qty = {} - {} = {} remaining'.format(oldqty,ordqty,qty))
        print(book)
        # remove used quote
        print('removing used quote {}'.format(bestid))
        del book[bestid]
        print(book)

    print('order completed')
    for exslice in slices:
        print(exslice)

    return slices

def quotetrimmer(side,limitprice,book):

    for quote in book.copy():
        quoteprice = book[quote][0]
        if compareprice(side,limitprice,quoteprice):
            print('removing quote {} from book as it does not meet limit price criteria'.format(quote))
            del book[quote]
    return book

def directedtrimmer(directedvenue,book):
    for quote in book.copy():
        venue = book[quote][2]
        if venue != directedvenue:
            print('removing quote {} from book as it does not meet directed venue criteria'.format(quote))
            del book[quote]
    return book
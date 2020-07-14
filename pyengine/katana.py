def matcher(qty,book):

    slices = []

    print(book)
    print(qty)

    while qty > 0:

        # if there's no quotes, we return whatever we got beforehand
        if len(book.keys()) == 0:
            print('no quotes left')
            return slices

        # all of these variables should be replaced by the best possible option
        lowestprice = 'none'
        lowestid = 'none'

        for quote in book.keys():
            print('trying quote {}'.format(quote))
            price = book[quote][0]

            # the first quote is always the lowest price
            if lowestprice == 'none':
                lowestprice = price

            if price <= lowestprice:
                print('{}:{} < {}:{}'.format(quote,price,lowestid,lowestprice))
                lowestprice = price
                lowestid = quote
                bqqty = book[quote][1]
                bexch = book[quote][2]

                ordqty = bqqty # in a normal case we use the full quote
                if bqqty > qty: # if we dont need the whole thing, we just use what we actually need
                    print('quote is larger than needed {}, will only use needed qty: {}'.format(qty,bqqty))
                    ordqty = qty

        exslice = '35=D;40=2;54=1;11={};38={};44={};57={};'.format(lowestid,ordqty,lowestprice,bexch)
        print(exslice)
        slices.append(exslice)

        oldqty = qty
        qty = qty - bqqty
        print('qty = {} - {} = {} remaining'.format(oldqty,ordqty,qty))

        # remove used quote
        print('removing used quote {}'.format(lowestid))

        print(lowestid)
        print(book)
        del book[lowestid]
        print(book)

    print('order completed')
    for exslice in slices:
        print(exslice)

    return slices

def quotetrimmer(limitprice,book):
    for quote in book.copy():
        quoteprice = book[quote][0]
        if quoteprice > limitprice:
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
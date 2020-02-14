def matcher(qty,book):

    slices = []
    slicefix = []

    print(book)
    print(qty)

    while qty > 0:

        # if there's no quotes, we return whatever we got beforehand
        if len(book.keys()) == 0:
            print('no quotes left')
            return slices

        # all of these variables should be replaced by the best possible option
        lowestprice = 100000 # todo - first quote we look at should be the lowest price as opposed to this arbitrary high number
        lowestid = 'none' # this becomes the quoteid of the best quote in the book
        quoteqty = 0

        for quote in book.keys():
            print('trying quote {}'.format(quote))
            price = book[quote][0]
            qqty = book[quote][1]
            exchange = book[quote][2]

            if price < lowestprice:
                print('{}:{} < {}:{}'.format(quote,price,lowestid,lowestprice))
                lowestprice = price
                lowestid = quote
                bqqty = book[quote][1]
                bexch = book[quote][2]

            ordqty = bqqty # in a normal case we use the full quote
            if bqqty > qty: # if we dont need the whole thing, we just use what we actually need
                ordqty = qty

        exslice = '35=D;40=2;54=1;11={};38={};44={};57={};'.format(lowestid,bqqty,lowestprice,bexch)
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
import json

def rl(logmsg):
    print('RAIN: {}'.format(logmsg))

def parse_schema(schema_file):
    rl('parsing {}'.format(schema_file))
    schemaraw = open(schema_file)
    schema = json.loads(schemaraw.read())
    schemaraw.close()
    rl('loaded schema')
    rl(schema)
    return schema

def process_order(client, qty):
    # check if client is in schema
    if client in schema.keys():
        rl('client found in schema, using assigned limit set')
        limitset = schema[client]
    else:
        rl('client not found in schema, using default limit set')
        limitset = schema['default']
    print(limitset)

    # max qty check
    maxqty = limitset[0]['MaxQty'] # ehhhhh
    rl('Order QTY: {} MaxQty: {}'.format(qty,maxqty))
    if qty > maxqty:
        rl('{} is greater than {} - maxqty check failed'.format(qty,maxqty))
        return False

    rl('all checks have passed!')
    return True


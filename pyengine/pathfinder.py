import json
import dfix

supported_types = ['single']

def pathfinder(routes):
    print(routes)
    routesparse = json.loads(routes)
    print(routesparse)
    routeid = routesparse['routeid']
    print('pathfinder: processing route \"{}\"'.format(routeid))
    if routesparse['type'] not in supported_types:
        print('pathfinder: invalid route type')
        return False
    elif routesparse['type'] == 'single':
        print('pathfinder: single destination routing')
        singledest = routesparse['destinations'][0]
        print(singledest)
        if singledest['available'] == 'yes':
            print('pathfinder: selected destination "{}"'.format(singledest['destination']))
            return singledest['destination']
        else:
            print('pathfinder: no destinations available')
            return False
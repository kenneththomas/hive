import json
import dfix

supported_types = ['single','priority']

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
            
    elif routesparse['type'] == 'priority':
        print('pathfinder: priority destination routing')
        priorityroutes = []
        for destination in routesparse['destinations']:
            
            # do not use routes which are not listed as available
            if destination['available'] == 'yes':
                priorityroutes.append(destination)
            else:
                print('pathfinder: {} is not available'.format(destination['destination']))
            
        # at this point, if there are no destinations available, we cannot use anything
        if len(priorityroutes) == 0:
            print('pathfinder: no destinations available!')
            return False

        bestpriority = 9999
        prioritydest = 'none'

        for openroute in priorityroutes:
            print(openroute['priority'])
            if openroute['priority'] < int(bestpriority):
                bestpriority = openroute['priority']
                prioritydest = openroute['destination']
            
        print('pathfinder: selected destination "{}"'.format(prioritydest))
        return prioritydest         
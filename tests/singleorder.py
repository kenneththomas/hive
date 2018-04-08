#used to test new features as we're building rather than to unit test
import sys

sys.path.insert(0, '../pyengine')
sys.path.insert(1, 'pyengine')
import hive

fix = '8=DFIX;11=4a4964c6;49=Tay;56=Spicii;35=D;55=ZVZZT;54=1;38=10000;44=10000;40=2;10=END'
execreport = hive.fixgateway(fix)
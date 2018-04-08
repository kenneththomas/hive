#used to test new features as we're building rather than to unit test
import sys

sys.path.insert(0, '../pyengine')
sys.path.insert(1, 'pyengine')
import hive
import dfix

fix = '8=DFIX;11=4a4964c6;49=Tay;56=Spicii;35=D;55=ZVZZT;54=1;38=300;44=1000;40=1;10=END'
fix = dfix.parsefix(fix)
execreport = hive.hundoslice(fix)

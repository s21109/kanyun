# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright 2012 Sina Corporation
# All Rights Reserved.
# Author: YuWei Peng <pengyuwei@gmail.com>
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import unittest
import time
import sys
import random
import mox
import pycassa
from collections import OrderedDict

from kanyun.server import api_server

class StatisticsTest(unittest.TestCase):

    def setUp(self):
        self.mox = mox.Mox()

    def tearDown(self):
        self.mox.UnsetStubs()
        
    def testStatistics(self):
        s = api_server.Statistics()
        isum = 0.0
        val = 1
        for i in range(1,11):
            isum += i
            s.update(i)
            print "%02d. value=%02d, sum=%02d, max=%02d, min=%02d, diff=%02d, agerage=%00.f" \
                % (i, i, s.get_sum(), s.get_max(), s.get_min(), s.get_diff(),  s.get_agerage())
            assert s.get_sum() == isum
            assert s.get_max() == i
            assert s.get_min() == 1
            assert s.get_agerage() == isum / i
        print "Statistics test \t\t\t[\033[1;33mOK\033[0m]"


def InitApiMox():
    pass
    
    
def ApiGetDataMox():
    ts = time.time()
    rs = {ts-180:1, ts-181:1, ts-120:2, ts-60:3, ts:5}
    rs = {
            time.mktime((2012, 4, 9, 12, 6, 1,0,0,0)): 1, \
            time.mktime((2012, 4, 9, 12, 6, 2,0,0,0)): 1, \
            time.mktime((2012, 4, 9, 12, 7, 1,0,0,0)): 2, \
            time.mktime((2012, 4, 9, 12, 8, 1,0,0,0)): 5, \
            time.mktime((2012, 4, 9, 12, 8, 2,0,0,0)): 1, \
            time.mktime((2012, 4, 9, 12, 8, 3,0,0,0)): 1, \
            time.mktime((2012, 4, 9, 12, 8, 4,0,0,0)): 1, \
            time.mktime((2012, 4, 9, 12, 8, 5,0,0,0)): 1, \
            time.mktime((2012, 4, 9, 12, 8, 6,0,0,0)): 1, \
            time.mktime((2012, 4, 9, 12, 9, 1,0,0,0)): 10, \
            time.mktime((2012, 4, 9, 12, 10, 1,0,0,0)): 20, \
            }
    rs = OrderedDict(sorted(rs.items(), key=lambda t: t[0]))
    return rs, len(rs), False
    
    
class ColumnFamilyMox():

    def __init__(self, a='', b=''):
        pass
    pass
    
    
class TestApiServer(unittest.TestCase):

    def setUp(self):
        self.mox = mox.Mox()
        
    def tearDown(self):
        self.mox.UnsetStubs()

    def testParamTypeCheck(self):
        row_id = None
        cf_str = None
        scf_str = None
        period = None
        statistic = None
        rs1, count, _ = api_server.api_statistic(None, None, None, None, period=5, time_from=0, time_to=0)
        rs2, count, _ = api_server.api_getbykey(None, cf_str, scf_str, limit=20000)
        rs3, count, _ = api_server.api_getbyInstanceID(row_id, cf_str)
        rs4, count, _ = api_server.api_getdata(row_id, cf_str, scf_str, time_from=0, time_to=0)
        rs5 = api_server.api_getInstancesList(None)
        rs6 = api_server.analyize_data(None, period, statistic)
        assert(rs1 is None)
        assert(rs2 is None)
        assert(rs3 is None)
        assert(rs4 is None)
        assert(rs5 is None)
        assert(rs6 is None)
        
        print "Param type test \t\t\t[\033[1;33mOK\033[0m]"
    
    def testApiGetdata(self):
        time.clock()
        row_id = 'instance-00000001@pyw.novalocal'
        time_from = 1332815400
        time_to = 0
        scf_str = 'total'
        cf_str = 'cpu'
                
        self.mox.StubOutWithMock(api_server, 'api_getdata')
        api_server.api_getdata(row_id, cf_str, scf_str, \
                time_from, time_to).AndReturn(ApiGetDataMox())
        self.mox.ReplayAll()
        
        rs, count, _ = api_server.api_getdata(row_id, cf_str, scf_str, time_from, time_to)
        self.mox.VerifyAll()
        print "%d results, spend %f seconds" % (count, time.clock())
        print "ApiGetdata test \t\t\t[\033[1;33mOK\033[0m]"
        print '-' * 60
    
    def testApiStatisticSUM(self):
        time.clock()
        row_id = u'instance-00000001@pyw.novalocal'
        period = 5
        time_from = 1332833464
        time_to = 0
        cf_str = u'cpu'
        scf_str = u'total'
        statistic = api_server.STATISTIC.SUM
        
        m = self.mox
        m.StubOutWithMock(api_server, 'api_getdata')
        api_server.api_getdata(row_id, cf_str, scf_str, \
                time_from, time_to).AndReturn(ApiGetDataMox())
        self.mox.ReplayAll()
        statistic = api_server.STATISTIC.SUM
        rs, count, _ = api_server.api_statistic(row_id, cf_str, scf_str, \
                statistic, period, \
                time_from, time_to)
        self.assertEqual(count, 1)
        self.assertEqual(rs.values()[0], 44)
        self.mox.VerifyAll()
        
        print "%d SUM results, spend %f seconds" % (count, time.clock())
        print "api_statistics sum test \t\t\t[\033[1;33mOK\033[0m]"
        print '-' * 60

    def testApiStatisticMAX(self):
        time.clock()
        row_id = u'instance-00000001@pyw.novalocal'
        period = 5
        time_from = 1332833464
        time_to = 0
        cf_str = u'cpu'
        scf_str = u'total'
        statistic = api_server.STATISTIC.MAXIMUM
        
        m = self.mox
        m.StubOutWithMock(api_server, 'api_getdata')
        api_server.api_getdata(row_id, cf_str, scf_str, \
                time_from, time_to).AndReturn(ApiGetDataMox())
        self.mox.ReplayAll()
        statistic = api_server.STATISTIC.MAXIMUM
        rs, count, _ = api_server.api_statistic(row_id, cf_str, scf_str, \
                statistic, period, \
                time_from, time_to)
        self.assertEqual(count, 1)
        self.assertEqual(rs.values()[0], 20)
        self.mox.VerifyAll()
        print "%d MAX results, spend %f seconds" % (count, time.clock())
        print "api_statistics max test \t\t\t[\033[1;33mOK\033[0m]"
        print '-' * 60
        
        
    def testApiStatisticMIN(self):
        time.clock()
        row_id = u'instance-00000001@pyw.novalocal'
        period = 5
        time_from = 1332833464
        time_to = 0
        cf_str = u'cpu'
        scf_str = u'total'
        statistic = api_server.STATISTIC.MINIMUM
        
        m = self.mox
        m.StubOutWithMock(api_server, 'api_getdata')
        api_server.api_getdata(row_id, cf_str, scf_str, \
                time_from, time_to).AndReturn(ApiGetDataMox())
        self.mox.ReplayAll()
        statistic = api_server.STATISTIC.MINIMUM
        rs, count, _ = api_server.api_statistic(row_id, cf_str, scf_str, \
                statistic, period, \
                time_from, time_to)
        self.assertEqual(count, 1)
        self.assertEqual(rs.values()[0], 1)
        self.mox.VerifyAll()
        
        print "%d MIN results, spend %f seconds" % (count, time.clock())
        print "api_statistics min test \t\t\t[\033[1;33mOK\033[0m]"
        print '-' * 60
    
    def testApiStatisticAVG(self):
        time.clock()
        row_id = u'instance-00000001@pyw.novalocal'
        period = 5
        time_from = 1332833464
        time_to = 0
        cf_str = u'cpu'
        scf_str = u'total'
        statistic = api_server.STATISTIC.AVERAGE
        
        m = self.mox
        m.StubOutWithMock(api_server, 'api_getdata')
        api_server.api_getdata(row_id, cf_str, scf_str, \
                time_from, time_to).AndReturn(ApiGetDataMox())
        self.mox.ReplayAll()
        statistic = api_server.STATISTIC.AVERAGE
        rs, count, _ = api_server.api_statistic(row_id, cf_str, scf_str, \
                statistic, period, \
                time_from, time_to)
        self.assertEqual(count, 1)
        self.mox.VerifyAll()
        
        print "%d AVERAGE results, spend %f seconds" % (count, time.clock())
        print "api_statistics AVERAGE test \t\t\t[\033[1;33mOK\033[0m]"
        print '-' * 60


if __name__ == '__main__':
    time.clock()
    ApiTestSuite = unittest.TestSuite()
    ApiTestSuite.addTest(StatisticsTest("testStatistics"))
    ApiTestSuite.addTest(TestApiServer("testParamTypeCheck"))
    ApiTestSuite.addTest(TestApiServer("testApiGetdata"))
    ApiTestSuite.addTest(TestApiServer("testApiStatisticSUM"))
    ApiTestSuite.addTest(TestApiServer("testApiStatisticMAX"))
    ApiTestSuite.addTest(TestApiServer("testApiStatisticMIN"))
    ApiTestSuite.addTest(TestApiServer("testApiStatisticAVG"))
    
    runner = unittest.TextTestRunner()
    runner.run(ApiTestSuite)

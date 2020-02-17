#!/usr/bin/env python
# coding=utf-8

import json
from aliyunsdkcore.client import AcsClient
from aliyunsdkalidns.request.v20150109.DescribeDomainRecordsRequest import DescribeDomainRecordsRequest

DomainName = "baidu.com"
client = AcsClient('<accessKeyId>', '<accessSecret>', 'cn-hangzhou')

request = DescribeDomainRecordsRequest()
request.set_accept_format('json')
request.set_DomainName(DomainName)
response = client.do_action_with_exception(request)
response = json.loads(response)
for i in response['DomainRecords']['Record']:
    print('RR:%s\tDomainName:%s\tRecordId:%s' % (i['RR'], i['DomainName'], i['RecordId']))

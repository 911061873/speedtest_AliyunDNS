#!/usr/bin/env python
# coding=utf-8
import json
import os
import speedtest
import time
from aliyunsdkalidns.request.v20150109.UpdateDomainRecordRequest import UpdateDomainRecordRequest
from aliyunsdkcore.client import AcsClient
from retrying import retry

default_config = {
    'test': {
        'servers': [],
        'threads': None,
        'num': 3,
        'wt_tm': 150,
        'thres': 50
    },
    'aliyun': {
        'AccessKeyId': 'AccessKeyId',
        'AccessKeySecret': 'AccessKeySecret',
        'region_id': 'region_id',
        'lastchange': '',
        'domains': [
            {'RecordId': '4020645678962688', 'RR': 'pan', 'Type': 'A',
             'set_Value': {'a': '1.1.1.1', 'b': '5.5.5.5'}},
            {'RecordId': '4020645678962688', 'RR': 'pan', 'Type': 'A',
             'set_Value': {'a': '2.2.2.2', 'b': '6.6.6.6'}},
            {'RecordId': '4020645678962688', 'RR': 'pan', 'Type': 'A',
             'set_Value': {'a': '3.3.3.3', 'b': '7.7.7.7'}},
            {'RecordId': '4020645678962688', 'RR': 'pan', 'Type': 'A',
             'set_Value': {'a': '4.4.4.4', 'b': '8.8.8.8'}}
        ]
    }
}  # 默认配置
downloads = []
uploads = []
config = {}
s = ''
client = ''


def read_config():
    """"读取配置"""
    with open("config.json") as json_file:
        conf = json.load(json_file)
    return conf


def update_config(conf):
    """"更新配置"""
    with open("config.json", 'w') as json_file:
        json.dump(conf, json_file, indent=4)
    return None


def new_print(old_print):
    def inner(*args, **kwargs):
        colors = {
            '红': '31',
            '绿': '32',
            '黄': '33',
            '蓝': '34',
            '紫': '35',
            '青': '36',
            '白': '37',
        }
        if 'color' in kwargs:
            if kwargs['color'] in colors:
                color = colors[kwargs['color']]
            else:
                color = '38'
        else:
            color = '32'
        old_print('\033[33m%s\033[0m' % time.strftime('[%m-%d %H:%M:%S]', time.localtime()), end='')
        old_print('\033[' + color + 'm', end='')
        old_print(*args, end='')
        old_print('\033[0m', **kwargs)

    return inner


print = new_print(print)


def retry_if_timeout(exception):
    return isinstance(exception, TimeoutError)


@retry(stop_max_attempt_number=3, wait_fixed=5000)
def test(download, upload, servers=[], threads=None):
    s.get_servers(servers)
    s.get_best_server()
    if download:
        try:
            s.download(threads=threads)
        except Exception as e:
            print('下载测速失败。错误信息：%s' % e, end='', color='红')
    if upload:
        try:
            s.upload(threads=threads)
        except Exception as e:
            print('上传测速失败。错误信息：%s' % e, end='', color='红')
    results_dict = s.results.dict()
    return {'download': results_dict['download'] / 1000000, 'upload': results_dict['upload'] / 1000000,
            'ping': results_dict['ping']}


@retry(stop_max_attempt_number=3, wait_fixed=2000)
def init_test():
    global s
    try:
        s = speedtest.Speedtest()
    except Exception as e:
        print('测速初始化失败。应该是网络问题导致的。', e)


def averagenum(speeds: list):
    num = 0
    sam = 0
    for i in speeds:
        if i:
            sam += i
            num += 1
    return sam / num


def update_domain(RecordId: str, RR: str, Type: str, Value: str):
    request = UpdateDomainRecordRequest()
    request.set_accept_format('json')
    request.set_RecordId(RecordId)
    request.set_RR(RR)
    request.set_Type(Type)
    request.set_Value(Value)
    try:
        client.do_action_with_exception(request)
    except Exception as e:
        print('修改%s解析失败' % RecordId, e)
    else:
        print('修改%s解析成功' % RecordId)


def main():
    global config, client
    if not os.path.exists('config.json'):
        update_config(default_config)
    config = read_config()
    client = AcsClient(config['aliyun']['AccessKeyId'], config['aliyun']['AccessKeySecret'],
                       config['aliyun']['region_id'])
    init_test()
    print('开始运行', end='\n\n')
    try:
        while True:
            # 测速
            print('*' * 50)
            for i in range(1, config['test']['num'] + 1):
                print("第%d次测速" % i)
                result = test(False, True, config['test']['servers'])
                if result['download']:
                    print('\t下载速度为%.2f Mbps' % result['download'])
                    print('*' * 30)
                    downloads.append(result['download'])
                if result['upload']:
                    print('\t上传速度为%.2f Mbps' % result['upload'])
                    print('*' * 30)
                    uploads.append(result['upload'])
                if i < config['test']['num']:
                    print('')
                    print('延时%d秒开始下一次测速' % config['test']['wt_tm'])
                    print('')
                    time.sleep(config['test']['wt_tm'])
                else:
                    print('测速完成')
                    print('*' * 50)

            # 判断
            if sum(downloads):
                down_aver = averagenum(downloads)
                print("下载平均速度为：%.2f Mbps" % down_aver)
            up_aver: float = 0
            if sum(uploads):
                up_aver = averagenum(uploads)
                print("上传平均速度为：%.2f Mbps" % up_aver)
            if up_aver < config['test']['thres']:
                print('测速平均值%f小于阀值%f，开始更换域名解析' % (up_aver, config['test']['thres']), color='黄')
                if config['aliyun']['lastchange'] == 'a' or config['aliyun']['lastchange'] == "":
                    for i in config['aliyun']['domains']:
                        update_domain(i['RecordId'], i['RR'], i['Type'], i['set_Value']['b'])
                    config['aliyun']['lastchange'] = 'b'
                    update_config(config)
                else:
                    print('已经切换到备用线路了，无需切换。', color='黄')
            else:
                if config['aliyun']['lastchange'] == 'b':
                    print('测速平均值%f达到阀值%f，切换回主线路' % (up_aver, config['test']['thres']), color='绿')
                    for i in config['aliyun']['domains']:
                        update_domain(i['RecordId'], i['RR'], i['Type'], i['set_Value']['a'])
                    config['aliyun']['lastchange'] = 'a'
                    update_config(config)
                else:
                    print('一切正常！')
            time.sleep(config['test']['wt_tm'])
    except KeyboardInterrupt:
        update_config(config)
        print('配置文件以保存，正在退出。')
        exit()


if __name__ == "__main__":
    main()

# speedtest_AliyunDNS
[![Build Status](https://travis-ci.org/911061873/speedtest_AliyunDNS.svg?branch=master)](https://travis-ci.org/911061873/speedtest_AliyunDNS)

这是一个自动检测网速，并判断是否切换到备用线路的脚本。
首次运行会在目录下生成config.json，也可从过参数`--makeconfig`创建配置文件。
## 配置
```
{
'test': {
        'servers': [],          //speed test服务器id，可填多个。为空自动获取最佳。
        'threads': None,        //测速线程，为空多线程
        'num': 3,               //测速次数，结果取平均值
        'wt_tm': 150,           //测速间隔时间（秒）
        'thres': 50             //速度切换阀值（Mbps）
    },
    'aliyun': {
        'AccessKeyId': 'AccessKeyId',
        'AccessKeySecret': 'AccessKeySecret',
        'region_id': 'region_id',
        'lastchange': '',
        'domains': [            //可添加多条线路，适用于同一线路的服务器。a为常用IP，b为备用IP。
            {'RecordId': '4020645678962688', 'RR': 'pan', 'Type': 'A',
             'set_Value': {'a': '1.1.1.1', 'b': '5.5.5.5'}},
            {'RecordId': '4020645678962688', 'RR': 'pan', 'Type': 'A',
             'set_Value': {'a': '2.2.2.2', 'b': '6.6.6.6'}}
        ]
    }
}
```



import speedtest

s = ''


def init_test():
    global s
    try:
        s = speedtest.Speedtest()
        print(s)
    except Exception as e:
        print('测速初始化失败。应该是网络问题导致的。', e)


def speed_test(download, upload, servers=[], threads=None):
    s.get_servers(servers=servers)
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


def test_answer():
    init_test()
    assert s != ''
    a = speed_test(True,True)
    assert len(a)
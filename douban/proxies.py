# IP地址取自国内髙匿代理IP网站：http://www.xicidaili.com/nn/
# 仅仅爬取首页IP地址就足够一般使用
import urllib.request

from bs4 import BeautifulSoup
import requests
import random

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}
def getHTMLText(url,proxies):
    try:
        r = requests.get(url,proxies=proxies)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
    except:
        return 0
    else:
        return r.text

def get_ip_list2():
    url = 'http://www.xicidaili.com/nn/'
    web_data = requests.get(url, headers)
    soup = BeautifulSoup(web_data.text, 'lxml')
    ips = soup('tr',class_='odd')
    ip_list = []
    for ip_info in ips:
        tds = ip_info('td')
        ip_list.append(tds[1].text + ':' + tds[2].text)


def get_ip_list(url):
    web_data = requests.get(url, headers)
    soup = BeautifulSoup(web_data.text, 'html')
    ips = soup.find_all('tr')
    ip_list = []
    for i in range(1, len(ips)):
        ip_info = ips[i]
        tds = ip_info.find_all('td')
        ip_list.append(tds[1].text + ':' + tds[2].text)

    return ip_list

def get_random_ip(ip_list):
    url = 'https://www.douban.com/group/people/2265373/'
    # 检测ip可用性，移除不可用ip：（这里其实总会出问题，你移除的ip可能只是暂时不能用，剩下的ip使用一次后可能之后也未必能用）
    for ip in ip_list:
        try:
            proxy_host1 = "https://" + ip
            proxy_host2 = "http://" + ip
            proxy_temp = {"https": proxy_host1,"http":proxy_host2}
            res = requests.get(url, proxies=proxy_temp)
            res.raise_for_status()
            proxies =
            # res = urllib.request.urlopen(url,proxies=proxy_temp).read()
        except Exception as e:
            continue
    proxies = {'http': proxy_ip}
    return proxies

if __name__ == '__main__':
    url = 'http://www.xicidaili.com/nn/'
    ip_list = get_ip_list(url)
    proxies = get_random_ip(ip_list)
    print(proxies)
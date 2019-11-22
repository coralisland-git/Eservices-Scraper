import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://eservices.cipc.co.za/Search.aspx'


def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.replace(u'\u2013', '-').encode('ascii', 'ignore').encode("utf8").replace("\r\n", ' ').strip()

def get_value(item):
    if item == None :
        item = ''
    item = validate(item)
    if item == '':
        item = ''
    return item

def eliminate_space(items):
    rets = []
    for item in items:
        item = validate(item)
        if item != '':
            rets.append(item)
    return rets

def parse_address(address):
    address = usaddress.parse(address)
    street = ''
    city = ''
    state = ''
    zipcode = ''
    for addr in address:
        if addr[1] == 'PlaceName':
            city += addr[0].replace(',', '') + ' '
        elif addr[1] == 'ZipCode':
            zipcode = addr[0].replace(',', '')
        elif addr[1] == 'StateName':
            state = addr[0].replace(',', '') + ' '
        else:
            street += addr[0].replace(',', '') + ' '
    return { 
        'street': get_value(street), 
        'city' : get_value(city), 
        'state' : get_value(state), 
        'zipcode' : get_value(zipcode)
    }

def complete(number):

    ret = str(number)

    for idx in range(0, 6-len(ret)):

        ret = '0'+ret

    return ret


def scrape():
    output_list = []
    session = requests.Session()
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': 'dtCookie=3$0DFB8CBA2B06892164F4B8B1F1B86CE2; ASP.NET_SessionId=lxtoia0jaepjhnhh4masihk2',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
        'X-MicrosoftAjax': 'Delta=true',
        'X-Requested-With': 'XMLHttpRequest'
    }

    count = 0
    url = "https://eservices.cipc.co.za/Search.aspx"
    typ_list = ['23', '07']
    # for year in range(1950, 2019):
    for year in range(1950, 2019):
        file_name = 'data/data_'+str(year)+'.json'
        with open(file_name, mode='w') as output_file:
            output_file.write('[')
            for typ in typ_list:
                for c_number in range(0, 1000000):
                    try:
                        s_key = str(year) + '/' + complete(c_number) + '/' + typ            
                        formdata = {
                            'ctl00$cntMain$ScriptManager1': 'ctl00$cntMain$Updatepanel1|ctl00$cntMain$lnkSearchIcon',
                            '__EVENTTARGET': 'ctl00$cntMain$lnkSearchIcon',
                            '__EVENTARGUMENT': '',
                            '__LASTFOCUS': '',
                            'ctl00_cntMain_TabContainer1_ClientState': '{"ActiveTabIndex":0,"TabEnabledState":[true,true,true,true],"TabWasLoadedOnceState":[true,false,false,false]}',
                            '__VIEWSTATE': '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AAwUKwAAZBgIBRtjdGwwMCRjbnRNYWluJFRhYkNvbnRhaW5lcjEPD2RmZAUwY3RsMDAkY250TWFpbiRUYWJDb250YWluZXIxJFRhYlBhbmVsNCRnZHZFbnRIaXN0DzwrAAwBCAIBZAUvY3RsMDAkY250TWFpbiRUYWJDb250YWluZXIxJFRhYlBhbmVsMyRnZHZBUlBhaWQPPCsADAEIAgFkBRxjdGwwMCRjbnRNYWluJGdkdkVudGVycHJpc2VzD2dkBTZjdGwwMCRjbnRNYWluJFRhYkNvbnRhaW5lcjEkVGFiUGFuZWwzJGdkdkFST3V0c3RhbmRpbmcPPCsADAEIAgFkBR5fX0NvbnRyb2xzUmVxdWlyZVBvc3RCYWNrS2V5X18WAQUbY3RsMDAkY250TWFpbiRUYWJDb250YWluZXIxBThjdGwwMCRjbnRNYWluJFRhYkNvbnRhaW5lcjEkVGFiUGFuZWwyJGdkdkRpcmVjdG9yRGV0YWlscw88KwAMAQgCAWQFFmN0bDAwJGNudE1haW4kZ2R2TmFtZXMPZ2QZIYzkDT97cYde9H/Kcd8inopXc4ngNDT6NSggzSdoBg==',
                            '__VIEWSTATEGENERATOR': 'BBBC20B8',
                            '__EVENTVALIDATION': '/wEdAAwZp7fw+NJdnkI8DxYoSCMzqKcmrSDkBpJ8st+qyoYoz0kB/raq3HkRgfiN0ajyvNTfVH8MoMP2yyP68NO6sbXD0FcfG0xn6OKsayQ1HyOKoaNWYjQf+O6+5QdIL7narmgz+JKhQ1Aqq9GfFXaYkloy5Sf36g4gDGAXKWKBOSO/mCSllWI9KqQcjdGA9nJKIH8X4hkjG+lSkwNWrdIxbtgrrAEaC2fHXmyy9M2Nl1i+8K/AJ/2jNE4ay7RfFFTTCKPrxbGR/4sEIw5S8VqSxco+DRAPinkKF7hIoqjvkSEICQ==',
                            'ctl00$cntMain$drpSearchOptions': 'EntNo',
                            'ctl00$cntMain$txtSearchCIPC': s_key,
                            'ctl00$cntMain$wtmkSearch_ClientState': '',
                            '__ASYNCPOST': 'true',
                        }
                        request = session.post(url, headers=headers, data=formdata)
                        headers2= {
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=',
                            'Cookie': 'dtCookie=3$0DFB8CBA2B06892164F4B8B1F1B86CE2; ASP.NET_SessionId=lxtoia0jaepjhnhh4masihk2',
                            'Upgrade-Insecure-Requests': '1',
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36'
                        }
                        request2 = session.get(url, headers=headers2)
                        source = etree.HTML(request2.text)
                        output = []
                        is_valid = len(source.xpath('.//div[@id="ctl00_cntMain_pnlEntNoSearch"]'))
                        if is_valid == 0:                            
                            count += 1
                            print(s_key, count)
                            if count > 200:
                                count = 0
                                break
                            continue
                        count = 0
                        director_list = source.xpath('.//table[@id="ctl00_cntMain_TabContainer1_TabPanel2_gdvDirectorDetails"]//tr')[1:]
                        directors = []
                        for director in director_list:
                            data = eliminate_space(director.xpath('.//text()'))
                            if len(data) >= 5:
                                directors.append({
                                    "Director ID/Passport Number" : data[0], 
                                    "Director Name" : data[1], 
                                    "Director Surname" : data[2], 
                                    "Director Type" : data[3], 
                                    "Director Status" : data[4],
                                })
                        filed_annuals = source.xpath('.//table[@id="ctl00_cntMain_TabContainer1_TabPanel3_gdvARPaid"]//tr')[1:]
                        filed_annual_returns = []
                        for filed in filed_annuals:
                            data = eliminate_space(filed.xpath('.//text()'))
                            if len(data) >= 5:
                                filed_annual_returns.append({
                                    "AR Year" : validate(data[0]),
                                    "Customer Code" : validate(data[1]),
                                    "Amount Paid" : validate(data[2]),
                                    "Tracking Number" :validate(data[3]),
                                    "Date Filed" : validate(data[4])
                                })                    
                        outstanding_annuals = source.xpath('.//table[@id="ctl00_cntMain_TabContainer1_TabPanel3_gdvAROutstanding"]//tr')[1:]
                        outstanding_annual_returns = []
                        for outstanding in outstanding_annuals:
                            data = eliminate_space(outstanding.xpath('.//text()'))
                            if len(data) >= 3:
                                outstanding_annual_returns.append({
                                    "AR Year" : validate(data[0]),
                                    "AR Month" : validate(data[1]),
                                    "AR Non-Compliance Date" : validate(data[2])
                                })

                        histories = source.xpath('.//table[@id="ctl00_cntMain_TabContainer1_TabPanel4_gdvEntHist"]//tr')[1:]
                        enterprise_history = []
                        for history in histories:
                            data = eliminate_space(history.xpath('.//text()'))
                            if len(data) >= 2:
                                enterprise_history.append({
                                    "Date" : validate(data[0]),
                                    "Details" : validate(data[1])
                                })
                        output = { 
                            "key" : s_key,
                            "Enterprise" : {
                                "Enterprise Number" : validate(source.xpath('.//span[@id="ctl00_cntMain_TabContainer1_TabPanel1_lblEntNo"]//text()')),
                                "Enterprise Name" : validate(source.xpath('.//span[@id="ctl00_cntMain_TabContainer1_TabPanel1_lblEntName"]//text()')),
                                "Enterprise Type" : validate(source.xpath('.//span[@id="ctl00_cntMain_TabContainer1_TabPanel1_lblEntType"]//text()')),
                                "Enterprise Status" : validate(source.xpath('.//span[@id="ctl00_cntMain_TabContainer1_TabPanel1_lblEntStatus"]//text()')),
                                "Compliance Notice Status" : validate(source.xpath('.//span[@id="ctl00_cntMain_TabContainer1_TabPanel1_lblNonComply"]//text()')),
                                "Registration Date" : validate(source.xpath('.//span[@id="ctl00_cntMain_TabContainer1_TabPanel1_lblRegDate"]//text()')),
                                "Physical Address" : validate(eliminate_space(source.xpath('.//span[@id="ctl00_cntMain_TabContainer1_TabPanel1_lblPhysAddress"]//text()'))), 
                                "Postal Address" : validate(eliminate_space(source.xpath('.//span[@id="ctl00_cntMain_TabContainer1_TabPanel1_lblPostalAddress"]//text()'))), 
                            },
                            "Director" : directors,
                            "Annual Return Details" : {
                                "Filed Annual Returns" : filed_annual_returns,
                                "Outstanding Annual Returns" : outstanding_annual_returns
                            },
                            "Enterprise history" : enterprise_history
                        }
                        # output_list.append(output)
                        output_file.write(json.dumps(output, sort_keys=True, indent=4) + ',')
                    except Exception as e:
                        pass
            output_file.write(']')        

scrape()

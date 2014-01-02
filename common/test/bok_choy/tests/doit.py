#!/usr/bin/env python
"""
Helpful base test case classes for testing the LMS.
"""
from uuid import uuid4
import requests
import os
import re
import json
from bs4 import BeautifulSoup

def main():

    # csrftoken = 'foo'


    username = 'test_{}'.format(uuid4().hex[:8])
    email = '{0}@example.com'.format(username)
    password = 'password'

    print username

    # method = 'post'
    # path = '/login_post'
    # url = '{}{}'.format('http://localhost:8001', path)
    # headers = {'content-type': 'application/json', 'X-CSRFToken': csrftoken}
    # data = {"email": email, "password": password, "honor_code": "true"}
    # cookies = dict(csrftoken=csrftoken)

    # resp = requests.request(
    #     method, url, data=json.dumps(data), headers=headers, cookies=cookies
    # )

    # This will create a user something like:
    # USER_NNNN@_dummy_test@mitx.mit.edu
    # PASS_NNNN
    #
    method = 'get'
    path = '/auto_auth?username={}&email={}&password={}'.format(username, email, password)
    url = '{}{}'.format('http://localhost:8001', path)

    resp = requests.request(method, url)

    cookies = requests.utils.dict_from_cookiejar(resp.cookies)
    sessionid = cookies.get('sessionid', '')
    csrftoken = cookies.get('csrftoken', 'foo')

    # method = 'get'
    # path = '/course'
    # url = '{}{}'.format('http://localhost:8001', path)
    # cookies = dict(csrftoken=csrftoken, sessionid=sessionid)
    # resp = requests.request(method, url, cookies=cookies)

    # #Welcome, USER_97!
    # soup = BeautifulSoup(resp.text)
    # welcome_msg = soup.find('h2', class_='title').text
    # parsed = re.match(u'Welcome, (?P<username>\w+)!', welcome_msg)
    # username = parsed.group('username')
    # print 'user: {}'.format(username)

    method = 'post'
    path = '/course'
    headers = {'content-type': 'application/json', 'X-CSRFToken': csrftoken, 'accept': 'application/json'}
    course_num = '{}'.format(uuid4().hex[:4])
    data = {"org":"OrgX","number":course_num,"display_name":"Test Course","run":"2014"}
    url = '{}{}'.format('http://localhost:8001', path)
    resp = requests.request(method, url, data=json.dumps(data), headers=headers, cookies=cookies)


    # from pdb import set_trace; set_trace()

    print 'done'

if __name__ == '__main__':
    main()

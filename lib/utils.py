import os
import config
import urllib
import urllib2
import re
import json

path_hash = {}
url_hash = {}

def error_handler(msg):

    if config.debug:
        print msg

def git_path(path):

    if not path_hash.has_key(path):
        command = "cd %s && git rev-parse --show-toplevel" % path
        path_hash[path] = os.popen(command).read().strip()
    return path_hash[path]
        
def github_url(endpoint, params = {}): 

    path = os.path.join(config.api_url, endpoint)
    if not params.has_key("access_token"):
        params["access_token"] = config.access_token
    # generate path by combining params with the base url
    path += "?%s" % urllib.urlencode(params)
    return path

def github_request(url, method = "get", data = None, limit = config.max_api_pages):

    global url_hash

    # check the hash
    if method == "get" and url_hash.has_key(url):
        return url_hash[url]

    status = False
    res = False
    try: 
        request = urllib2.Request(url)
        request.get_method = lambda: method.upper()
        res = urllib2.urlopen(request)
        res_hash = json.loads(res.read())
        res_headers = res.info()
        status = True
    except urllib2.URLError as e:
        res = e
    except urllib2.HTTPError as e:
        res = e
    except any as e:
        res = e
    if not status:
        return res, status

    # hash the current value
    url_hash[url] = res # hash
    if limit == 0 or not "link" in res_headers.keys():
        return res, status

    # handle the complex hashing to combine all results
    next_url_match = re.match(r"<(?P<next_url>[^>]+)>; rel=\"next\"", res_headers['Link'])
    last_url_match = re.match(r"rel=\"last\"", res_headers['Link'])
    if not next_url_match or last_url_match:
        break
        url = next_url_match.group('next_url')
        print res_headers["Link"]
        print "TEST"
        sub_hash, sub_status = github_request(url, method, None, limit - 1)
        if not sub_status:
            return sub_hash, sub_status
        # extend the hash as needed

    return res_hash, status







import urllib2, cookielib, gzip, StringIO, os, time, re, htmlentitydefs, logging
from htmlentitydefs import name2codepoint as n2cp

cookie_jar       = cookielib.CookieJar()
cookie_processor = urllib2.HTTPCookieProcessor(cookie_jar)

ie7 = {
    'opener' : urllib2.build_opener(cookie_processor),
    'header' : {
        'User-Agent'      : 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)',
        'Accept-encoding' : 'gzip',
		'Accept'          : 'text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5',
		'Accept-Language' : 'en-us,en;q=0.5',
		'Accept-Charset'  : 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'
    }
}

def url(source, browser = ie7, charset = 'cp1252'):
    logging.debug("url: " + source)
    request = urllib2.Request(source, None, browser.get('header'))
    response = browser.get('opener', urllib2.build_opener()).open(request)
    data = response.read()

    if hasattr(response, 'headers'):
        # Handle GZIP
        if response.headers.get('content-encoding') == 'gzip':
            data = gzip.GzipFile(fileobj = StringIO.StringIO(data)).read()

        # Handle charset. CP1252 (superset of ISO-8859-1) is the default
        for param in response.headers.get('content-type', '').split(';')[1:]:
            if param.strip().startswith('charset='):
                charset = param.strip()[8:]
                break
        data = data.decode(charset)

    response.close()
    return data

def url_or_file(source, file, days = 1, browser = ie7, charset = 'cp1252'):
    logging.debug("urlfile: " + file)
    result = ''
    if os.path.isfile(file) and os.stat(file).st_size > 0 and time.time() - os.stat(file).st_mtime < days * 86400:
        result = uread(file)
    else:
        try:
            result = url(source, browser, charset)
            uwrite(file, result)
        except (urllib2.URLError, urllib2.HTTPError), err:
            errstr = str(err)
            logging.warn("url: " + source + ": " + errstr)
            if errstr[:12] is not 'HTTP Error 404':
                if os.path.isfile(file):
                    result = uread(file)

    return result

def uread(file, encoding='utf8'):
    ''' Reads'''
    file_handle = open(file)
    result = file_handle.read().decode(encoding)
    file_handle.close()
    return result

def uwrite(file, data, encoding='utf8'):
    file_handle = open(file, 'wb')
    file_handle.write(data.encode(encoding))
    file_handle.close()
    return data


# http://snippets.dzone.com/posts/show/4569
# Modified to handle hexadecimal (&#xH) entities as per http://www.w3.org/TR/REC-html40/charset.html
def substitute_entity(match):
    ent = match.group(3)
    if match.group(1) == "#":
        if match.group(2) == "x":
            return unichr(int(ent, 16))
        else:
            return unichr(int(ent))
    else:
        cp = htmlentitydefs.name2codepoint.get(ent)
        if cp:
            return unichr(cp)
        else:
            return match.group()

def decode_entities(string):
    entity_re = re.compile("&(#?)(x?)(\d{1,5}|\w{1,8});")
    return entity_re.subn(substitute_entity, string)[0]

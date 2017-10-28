import random
import platform

from pathenv import get_path

from bs4 import BeautifulSoup
from selenium import webdriver


class Chrome:
    def __init__(self, mobile=False):
        """
        Selenium Driver Init
        """
        chromedriver_location = get_path('driver', platform.system(), 'chromedriver')

        # [Option Lists] http://www.assertselenium.com/java/list-of-chrome-driver-command-line-arguments/
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--dns-prefetch-disable')
        chrome_options.add_argument('--no-sandbox')
        # chrome_options.add_argument('--net-log-capture-mode')

        if mobile:
            user_agent = [
                'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/60.0.3112.113 Mobile Safari/537.36',
                'Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, '
                'like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19'
            ]
            mobile_emulation = {
                'deviceMetrics': {'width': 360, 'height': 640, 'pixelRatio': 3.0},
                'userAgent': random.choice(user_agent)
            }
            chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)

        self.browser = webdriver.Chrome(chromedriver_location, chrome_options=chrome_options)

    def __call__(self):
        return self.browser

    def ajax_request(self, method, url, payload=None, header=None):
        if header:
            headers = [x.split(': ', 1) for x in header.strip().split('\n')][1:]
            ajax_headers_script = '\n'.join(['xhr.setRequestHeader("{0}", "{1}");'.format(*h) for h in headers])
        else:
            ajax_headers_script = ''

        if payload:
            if isinstance(payload, str):
                pass
            else:
                # dictionary format
                payload = '&'.join('{}={}'.format(k, v) for k, v in payload.items())

        ajax_script = '''
var done = arguments[0];

function fetch(method, url, payload) {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4 && xhr.status === 200) {
            done(xhr.responseText);
        }
    };
    xhr.open(method, url, true);
    
%s
    
    xhr.send(payload);
}
        ''' % ajax_headers_script

        ajax_script = '\n'.join([
            ajax_script,
            '''fetch({})'''.format(', '.join('"{}"'.format(x) for x in [method, url, payload] if x))
        ])

        print(ajax_script)

        self.browser.set_script_timeout(5)
        return BeautifulSoup(self.browser.execute_async_script(ajax_script), 'html.parser')

    def close(self):
        if self.browser is not None:
            if self.browser.get_cookies():
                self.browser.delete_all_cookies()
            self.browser.quit()

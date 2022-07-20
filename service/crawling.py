import os
import re


import requests
from bs4 import BeautifulSoup

from utils.utils import read_file_yaml
from utils.constants import CONFIG_CRAWL_FILE_PATH

class Crawler(object):
    def __init__(self, config_file_path=CONFIG_CRAWL_FILE_PATH, *args, **kwargs):
        
        current_path = os.path.abspath(os.getcwd())
        config_file_path = os.path.join(current_path, config_file_path)
        self.config = read_file_yaml(config_file_path)
    def url_parse_html(self, url):
        try:
            html = requests.get(url).text # => str, not bytes
            soup = BeautifulSoup(html, "html.parser")
            return soup
        except AssertionError as e:
            print(e)
    
    def get_domain_name(self, url):
        domain_name = re.split("\/+", url)[1]
        return domain_name

    def get_content_from_url(self, url):
        domain_name = self.get_domain_name(url)
        content_text = []

        for art in self.config['Articles']:
            if domain_name in art:
                soup = self.url_parse_html(url)
                if art[domain_name][1]['content_tag'] and art[domain_name][2]['content_class'] and art[domain_name][3]['content_id']:
                    content = soup.findAll(art[domain_name][1]['content_tag'],
                                        class_=art[domain_name][2]['content_class'],
                                        id_=art[domain_name][3]['content_id'])[-1]
                elif art[domain_name][1]['content_tag'] and art[domain_name][2]['content_class']:
                    content = soup.findAll(art[domain_name][1]['content_tag'],
                                        class_=art[domain_name][2]['content_class'])[-1]
                elif art[domain_name][1]['content_tag'] and art[domain_name][3]['content_id']:
                    content = soup.findAll(art[domain_name][1]['content_tag'],
                                        class_=art[domain_name][3]['content_id'])[-1]
                if content:
                    subcontent = content.find_all(art[domain_name][4]['content_text_tag'])
                    for s in subcontent:
                        content_text.extend(
                            s.text.strip().split('\n')
                        )
        return content_text


GET_METHOD = 'get'
POST_METHOD = 'post'
GENERAL_URL = 'https://trends.google.com/trends/api/explore'
INTEREST_OVER_TIME_URL = 'https://trends.google.com/trends/api/widgetdata/multiline'
INTEREST_BY_REGION_URL = 'https://trends.google.com/trends/api/widgetdata/comparedgeo'
RELATED_QUERIES_URL = 'https://trends.google.com/trends/api/widgetdata/relatedsearches'
TRENDING_SEARCHES_URL = 'https://trends.google.com/trends/hottrends/visualize/internal/data'
TOP_CHARTS_URL = 'https://trends.google.com/trends/api/topcharts'
SUGGESTIONS_URL = 'https://trends.google.com/trends/api/autocomplete/'
CATEGORIES_URL = 'https://trends.google.com/trends/api/explore/pickers/category'
TODAY_SEARCHES_URL = 'https://trends.google.com/trends/api/dailytrends'
REALTIME_TRENDING_SEARCHES_URL = 'https://trends.google.com/trends/api/realtimetrends'
ERROR_CODES = (500, 502, 504, 429)


HOST_LOCATE = 'vi-vn'
TIME_ZONE = 360
GEOGRAPHY = ''
TIME_OUT = (2, 5)
PROXIES = ''
RETRIES = 0
BACKOFF_FACTOR = 0
REQUEST_ARGS = None




DEFAULT_ENCODING = "utf-8"
TCP_PROTOCOL = "TCP"
DEFAULT_SERVER_INTERFACE = "0.0.0.0"
DEFAULT_SERVER_PORT = 6000
DEFAULT_RESPONSE_TIMEOUT = 60 * 60  # 1 hour
DEFAULT_SANIC_WORKERS = 1
ENV_SANIC_WORKERS = "SANIC_WORKERS"
ENV_SANIC_BACKLOG = "SANIC_BACKLOG"
ENV_LOG_LEVEL_LIBRARIES = "LOG_LEVEL_LIBRARIES"
DEFAULT_LOG_LEVEL_LIBRARIES = "ERROR"
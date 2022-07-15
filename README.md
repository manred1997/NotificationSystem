# Notification System
The system would be as following
![image](asset/system.png)



### Installation

Clone this repo and install the dependencies:

```bash

```
### Prepare data:

### Run service locally

```bash
python run.py
```
### Run service with docker
```bash
# build service

# run service

# stop service

```
### Usage:

```python
import requests
url = 'http://0.0.0.0:6000/get_trend_article'
results = requests.get(url)

print(results)
print(results.json())
```

Output:
```json
[
    {
        "image": {
            "newsUrl": "",
            "source": "",
            "imgUrl": "",
            "shareUrl": "",
            "articles": [
                {
                    "articleTitle": "",
                    "url": "",
                    "source": "",
                    "time": "",
                    "snippet": "",
                },
                {}
            ]
        }
    },
    {}
]
```

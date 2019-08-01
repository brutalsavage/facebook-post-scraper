# Facebook Scraper Selenium

Scrape Facebook Public Posts without using Facebook API 

## What It can Do

- Scrape Public Post Text
- Scrape Likes and Top 3 React Numbers
- Scrape Public Post Comments 

## Install Requirements

please make sure chrome is installed
```sh
pip install -r requirements.txt
```

## Usage

#### 1. Use scraper.py to print to screen or to file

```
usage: scraper.py [-h] -page PAGE -email EMAIL -password PASSWORD -len LEN
                  -infinite INFINITE [-usage USAGE]

Facebook Page Scraper

optional arguments:
  -h, --help            show this help message and exit

required arguments:
  -page PAGE, -p PAGE   The Facebook Public Page you want to scrape
  -email EMAIL, -e EMAIL
                        Facebook account email
  -password PASSWORD, -pass PASSWORD
                        Facebook account password
  -len LEN, -l LEN      Number of Posts you want to scrape
  -infinite INFINITE, -i INFINITE
                        Scroll until the end of the page (1 = infinite)
  -usage USAGE, -u USAGE
                        What to do with the data:Print on Screen (PS), Write
                        to Text File (WT)
```

Example: ```python scraper.py -page nytimes -email user@mail.com -password 123456 -len 1 -infinite 0 -usage WT```

#### 2. Use ```extract()``` to grab list of posts for additional parsing

```
from scraper import extract

list = extract(page, email, etc..)

# do what you what with the list 
```

Return value of ```extract()``` :

```python
[
{'Post': 'Text text text text text....',
 'Comments': {
        'name1' : 'Text text...',
        'name2' : 'Text text...',
         ...
         },
 'Reaction' : { # Reaction only contains the top3 reactions
        'LIKE' : int(number_of_likes),
        'HAHA' : int(number_of_haha),
        'WOW'  : int(number_of_wow)
         }}
  ...
]
```

### Note:

- Please use this code for Educational purposes only
- Will continue to add additional features and data


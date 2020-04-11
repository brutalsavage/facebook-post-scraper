# Facebook Scraper Selenium

Scrape Facebook Public Posts without using Facebook API 

## What It can Do

- Scrape Public Post Text
    - Raw Text
    - Picture
    - Link
- Scrape Likes and Top 3 React Numbers
- Scrape Public Post Comments 
    - Links in Comments
    - Pictures in Comments

## Install Requirements

Please make sure chrome is installed and ```chromedriver``` is placed in the same directory as the file

Find out which version of ```chromedriver``` you need to download in this link [Chrome Web Driver](http://chromedriver.chromium.org/downloads).

Place your Facebook login in info into ```facebook_credentials.txt```

Optional:
To download all videos from a specific page, make sure that [youtube-dl](https://github.com/ytdl-org/youtube-dl/) binary is downloaded locally.


```sh
pip install -r requirements.txt
```

## Usage

#### 1. Use scraper.py to print to screen or to file

```
usage: scraper.py [-h] -page PAGE -len LEN [-infinite INFINITE] [-usage USAGE]
                  [-comments COMMENTS]

Facebook Page Scraper

optional arguments:
  -h, --help            show this help message and exit

required arguments:
  -page PAGE, -p PAGE   The Facebook Public Page you want to scrape
  -len LEN, -l LEN      Number of Posts you want to scrape

optional arguments:
  -infinite INFINITE, -i INFINITE
                        Scroll until the end of the page (1 = infinite)
                        (Default is 0)
  -usage USAGE, -u USAGE
                        What to do with the data: Print on Screen (PS), Write
                        to Text File (WT) (Default is WT)
  -comments COMMENTS, -c COMMENTS
                        Scrape ALL Comments of Posts (y/n) (Default is n).
                        When enabled for pages where there are a lot of
                        comments it can take a while

```

#### 2. Use ```extract()``` to grab list of posts for additional parsing

```
from scraper import extract

list = extract(page, len, etc..)

# do what you want with the list 
```

Return value of ```extract()``` :

```python
[
{'Post': 'Text text text text text....',
 'Link' : 'https://link.com',
 'Image' : 'https://image.com',
 'Comments': {
        'name1' : {
            'text' : 'Text text...',
            'link' : 'https://link.com',
            'image': 'https://image.com'
         }
        'name2' : {
            ...
            }
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

#### 3. Use ```download_entire_page_videos``` to download all videos from a specific Facebook page
Example:
```
download_entire_page_videos.py --chromedriver chromedriver.exe --youtube_dl youtube-dl.exe --fbpage https://www.facebook.com/groups/[GROUP_ID]/ --numofposts 100
```

### Note:

- Please use this code for Educational purposes only
- Will continue to add additional features and data
    - ~comment chains scraping~
    - comment reaction scraping
    - different comment display (Most Relevant, New, etc)

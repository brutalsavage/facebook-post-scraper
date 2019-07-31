import json
import sys
sys.path.insert(1, '../../facebook-scraper')

from facebook_scraper import get_posts


import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup as bs


# for post in get_posts('newubcconfessions', pages=20):
#      print(post['post_id'])
#print(get_posts('nytimes', pages=1))


def extract_text():
    browser = webdriver.Chrome(ChromeDriverManager().install())

    browser.get("http://facebook.com")
    browser.maximize_window()
    browser.find_element_by_name("email").send_keys("secret")
    browser.find_element_by_name("pass").send_keys("secret")
    browser.find_element_by_id('loginbutton').click()
    browser.get("http://facebook.com/newubcconfessions/posts")
    lenOfPage = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    # time.sleep(5)
    # browser.find_element_by_id('expanding_cta_close_button').click()
    print(lenOfPage)
    lenOfPage = 1
    lastCount =0
    match=False
    while(match==False):
        #lastCount = lenOfPage
        lastCount+=1
        time.sleep(5)
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")

        print(lenOfPage)
        if lastCount==lenOfPage:
            match=True

    moreComments = browser.find_elements_by_xpath('//a[@data-testid="UFI2CommentsPagerRenderer/pager_depth_0"]')
    print(len(moreComments))
    for moreComment in moreComments:
        action = webdriver.common.action_chains.ActionChains(browser)
        action.move_to_element_with_offset(moreComment,5,5)
        action.perform()
        moreComment.click()



    time.sleep(100)

    # Now that the page is fully scrolled, grab the source code.
    source_data = browser.page_source

    # Throw your source into BeautifulSoup and start parsing!
    bs_data = bs(source_data, 'html.parser')
    k = bs_data.find_all(class_="_5pcr userContentWrapper")
    postBigDict = dict()

    allText = ""
    currentParagraph = 0

    for item in k:
        actualPosts = item.find_all(attrs={"data-testid": "post_message"})

        for posts in actualPosts:
            paragraphs = posts.find_all('p')
            currentParagraph+=1
            postBigDict[currentParagraph] = {}
            text = ""

            for index in range(0,len(paragraphs)):
                text+=paragraphs[index].text
                allText+=paragraphs[index].text

            postBigDict[currentParagraph]['Text'] = text

        toolBar = item.find_all(attrs={"role": "toolbar"})

        if not toolBar: # pretty fun
            continue

        postDict = dict()
        for toolBar_child in toolBar[0].children:

            str = toolBar_child['data-testid']
            reaction = str.split("UFI2TopReactions/tooltip_")[1]

            postDict[reaction] = 0

            for toolBar_child_child in toolBar_child.children:

                num = toolBar_child_child['aria-label'].split()[0]
                if 'K' in num:
                    realNum = float(num[:-1])*1000
                else:
                    realNum = float(num)

                postDict[reaction] = realNum

        print(postDict)
        postBigDict[currentParagraph]['Reaction'] = postDict

    browser.close()
    return postBigDict, allText

extract_text()
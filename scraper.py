import argparse
import time
import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as bs


def _extract_html(bs_data):
    k = bs_data.find_all(class_="_5pcr userContentWrapper")
    postBigDict = list()

    for item in k:
        actualPosts = item.find_all(attrs={"data-testid": "post_message"})
        postDict = dict()
        for posts in actualPosts:
            paragraphs = posts.find_all('p')
            text = ""
            for index in range(0, len(paragraphs)):
                text += paragraphs[index].text

            postDict['Post'] = text

        postComments = item.find_all(attrs={"data-testid": "UFI2Comment/body"})
        postDict['Comments'] = dict()

        for comment in postComments:
            commenter = comment.find(class_="_6qw4").text
            comment_text = comment.find("span", class_="_3l3x").text
            postDict['Comments'][commenter] = comment_text

        toolBar = item.find_all(attrs={"role": "toolbar"})

        if not toolBar:  # pretty fun
            continue

        postDict['Reaction'] = dict()

        for toolBar_child in toolBar[0].children:

            str = toolBar_child['data-testid']
            reaction = str.split("UFI2TopReactions/tooltip_")[1]

            postDict['Reaction'][reaction] = 0

            for toolBar_child_child in toolBar_child.children:

                num = toolBar_child_child['aria-label'].split()[0]
                if 'K' in num:
                    realNum = float(num[:-1]) * 1000
                else:
                    realNum = float(num)

                postDict['Reaction'][reaction] = realNum

        postBigDict.append(postDict)

    return postBigDict


def extract(page, numOfPost, email, password, infinite_scroll=False):
    option = Options()

    option.add_argument("--disable-infobars")
    option.add_argument("start-maximized")
    option.add_argument("--disable-extensions")

    # Pass the argument 1 to allow and 2 to block
    option.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 1
    })

    browser = webdriver.Chrome(executable_path="./chromedriver", chrome_options=option)
    browser.get("http://facebook.com")
    browser.maximize_window()
    browser.find_element_by_name("email").send_keys(email)
    browser.find_element_by_name("pass").send_keys(password)
    browser.find_element_by_id('loginbutton').click()

    browser.get("http://facebook.com/" + page + "/posts")

    if infinite_scroll:
        lenOfPage = browser.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    else:
        # roughly 8 post per scroll kindaOf
        lenOfPage = int(numOfPost / 8)

    print("Number Of Scrolls Needed " + str(lenOfPage))

    lastCount = -1
    match = False

    while not match:
        if infinite_scroll:
            lastCount = lenOfPage
        else:
            lastCount += 1

        # wait for the browser to load, this time can be changed slightly ~3 seconds with no difference, but 5 seems
        # to be stable enough
        time.sleep(5)

        if infinite_scroll:
            lenOfPage = browser.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return "
                "lenOfPage;")
        else:
            browser.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return "
                "lenOfPage;")

        if lastCount == lenOfPage:
            match = True

    # click on all the comments to scrape them all!
    # TODO: need to add more support for additional second level comments
    # TODO: ie. comment of a comment

    moreComments = browser.find_elements_by_xpath('//a[@data-testid="UFI2CommentsPagerRenderer/pager_depth_0"]')

    print("Scrolling through to click on more comments")

    while len(moreComments) != 0:
        for moreComment in moreComments:
            action = webdriver.common.action_chains.ActionChains(browser)
            try:
                # move to where the comment button is
                action.move_to_element_with_offset(moreComment, 5, 5)
                action.perform()
                moreComment.click()
            except:
                # do nothing right here
                pass

        moreComments = browser.find_elements_by_xpath('//a[@data-testid="UFI2CommentsPagerRenderer/pager_depth_0"]')

    # time.sleep(100)

    # Now that the page is fully scrolled, grab the source code.
    source_data = browser.page_source

    # Throw your source into BeautifulSoup and start parsing!
    bs_data = bs(source_data, 'html.parser')

    postBigDict = _extract_html(bs_data)
    browser.close()

    return postBigDict


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Facebook Page Scraper")
    required_parser = parser.add_argument_group("required arguments")
    required_parser.add_argument('-page', '-p', help="The Facebook Public Page you want to scrape", required=True)
    required_parser.add_argument('-email', '-e', help="Facebook account email", required=True)
    required_parser.add_argument('-password', '-pass', help="Facebook account password", required=True)
    required_parser.add_argument('-len', '-l', help="Number of Posts you want to scrape", type=int, required=True)
    required_parser.add_argument('-infinite', '-i', help="Scroll until the end of the page (1 = infinite)", type=int,
                                 required=True)
    required_parser.add_argument('-usage', '-u', help="What to do with the data:"
                                                      "Print on Screen (PS), "
                                                      "Write to Text File (WT)")
    args = parser.parse_args()

    infinite = False
    if args.infinite == 1:
        infinite = True

    postBigDict = extract(page=args.page, numOfPost=args.len, email=args.email, password=args.password,
                          infinite_scroll=infinite)

    if args.usage == "WT":
        with open('output.txt', 'w') as file:
            for post in postBigDict:
                file.write(json.dumps(post))  # use json load to recover
    else:
        print(postBigDict)

    print("Finished")

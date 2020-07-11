import argparse
import time
import json
import csv
import pickle

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as bs


with open('facebook_credentials.txt') as file:
    EMAIL = file.readline().split('"')[1]
    PASSWORD = file.readline().split('"')[1]


def _extract_post_creation_datetime(item):
    return item.find(class_="_5ptz")["title"]


def _extract_post_creator(item):
    return item.find(class_="_s0 _4ooo _5xib _5sq7 _44ma _rw img")["aria-label"]


def _extract_post_text(item):
    actualPosts = item.find_all(attrs={"data-testid": "post_message"})
    text = ""
    if actualPosts:
        for posts in actualPosts:
            paragraphs = posts.find_all('p')
            for index in range(0, len(paragraphs)):
                text += paragraphs[index].text
            text += ' -- '
    text = text[:-4]
    return text


def _extract_link(item):
    postLinks = item.find_all(class_="_6ks")
    link = ""
    for postLink in postLinks:
        link = postLink.find('a').get('href')
    return link


def _extract_post_id(item):
    postIds = item.find_all(class_="_5pcq")
    post_id = ""
    for postId in postIds:
        post_id = f"https://www.facebook.com{postId.get('href')}"
    return post_id


def _extract_image(item):
    postPictures = item.find_all(class_="scaledImageFitWidth img")
    image = ""
    for postPicture in postPictures:
        image = postPicture.get('src')
    return image


def _extract_like_count(item):
    likes = 0
    count = item.find(class_="_81hb")
    if count is not None:
        likes = int(count.text)
    return likes


def _extract_comment_count(item):
    comments = 0
    s = item.find(class_="_3hg- _42ft")
    if s is not None:
        comments = int(s.text.split(' ')[0])
    return comments


def _extract_share_count(item):
    shares = 0
    s = item.find(class_="_3rwx _42ft")
    if s is not None:
        shares = int(s.text.split(' ')[0])
    return shares


def _extract_comments(item):
    comments = []
    commentList = item.find('ul', {'class': '_7791'})
    if commentList:
        comment = commentList.find_all('li')
        if comment:
            for litag in comment:
                aria = litag.find(attrs={"aria-label": "Comment"})
                if aria:
                    thread = dict()
                    thread["comment"] = dict()

                    commenter = aria.find(class_="_6qw4").text
                    thread["comment"]["author"] = commenter

                    comment_text = litag.find("span", class_="_3l3x")
                    if comment_text:
                        thread["comment"]["text"] = comment_text.text

                    comment_link = litag.find(class_="_ns_")
                    if comment_link is not None:
                        thread["comment"]["link"] = comment_link.get("href")

                    comment_pic = litag.find(class_="_2txe")
                    if comment_pic is not None:
                        thread["comment"]["image"] = comment_pic.find(class_="img").get("src")

                    repliesList = litag.find(class_="_2h2j")
                    if repliesList:
                        reply = repliesList.find_all('li')
                        if reply:
                            thread['replies'] = []
                            for litag2 in reply:
                                aria2 = litag2.find(attrs={"aria-label": "Comment reply"})
                                if aria2:
                                    author = aria2.find(class_="_6qw4").text
                                    if author:
                                        reply_dict = dict()
                                        reply_dict["author"] = author

                                        reply_text = litag2.find("span", class_="_3l3x")
                                        if reply_text:
                                            reply_dict["text"] = reply_text.text

                                        r_link = litag2.find(class_="_ns_")
                                        if r_link is not None:
                                            reply_dict["link"] = r_link.get("href")

                                        r_pic = litag2.find(class_="_2txe")
                                        if r_pic is not None:
                                            reply_dict["image"] = r_pic.find(class_="img").get("src")

                                        thread['replies'].append(reply_dict)
                    comments.append(thread)
    return comments


def _extract_reaction(item):
    toolBar = item.find_all(attrs={"role": "toolbar"})

    if not toolBar:  # pretty fun
        return
    reaction = dict()
    for toolBar_child in toolBar[0].children:
        str = toolBar_child['data-testid']
        reaction = str.split("UFI2TopReactions/tooltip_")[1]

        reaction[reaction] = 0

        for toolBar_child_child in toolBar_child.children:

            num = toolBar_child_child['aria-label'].split()[0]

            # fix weird ',' happening in some reaction values
            num = num.replace(',', '.')

            if 'K' in num:
                realNum = float(num[:-1]) * 1000
            else:
                realNum = float(num)

            reaction[reaction] = realNum
    return reaction


def _login(browser, email, password):
    browser.get("http://facebook.com")
    browser.maximize_window()
    browser.find_element_by_name("email").send_keys(email)
    browser.find_element_by_name("pass").send_keys(password)
    browser.find_element_by_id('loginbutton').click()
    time.sleep(5)


def _count_needed_scrolls(browser, infinite_scroll, numOfPost):
    if infinite_scroll:
        lenOfPage = browser.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;"
        )
    else:
        # roughly 8 post per scroll kindaOf
        lenOfPage = int(numOfPost / 8)
    print("Number Of Scrolls Needed " + str(lenOfPage))
    return lenOfPage


def _scroll(browser, infinite_scroll, lenOfPage):
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


def parse_html(source_data, source_file=None):

    if source_file:

        # Load the source data from disk
        print(f"Loading the page source from {source_file}.")
        f = open(source_file,'rb')
        source_data = pickle.load(f)

    # Throw your source into BeautifulSoup and start parsing!
    bs_data = bs(source_data, 'html.parser')

    # Add to check
    with open('./bs.html',"w", encoding="utf-8") as file:
        file.write(str(bs_data.prettify()))

    k = bs_data.find_all(class_="_5pcr userContentWrapper")
    postBigDict = list()

    posts_processed = 0
    for item in k:
        postDict = dict()
        postDict['Datetime'] = _extract_post_creation_datetime(item)
        postDict['Creator'] = _extract_post_creator(item)
        postDict['Post'] = _extract_post_text(item)
        postDict['Link'] = _extract_link(item)
        postDict['PostId'] = _extract_post_id(item)
        postDict['Image'] = _extract_image(item)
        postDict['NumComments'] = _extract_comment_count(item)
        postDict['NumShares'] = _extract_share_count(item)
        postDict['NumLikes'] = _extract_like_count(item)
        postDict['Comments'] = _extract_comments(item)
        # postDict['Reaction'] = _extract_reaction(item)

        # Add to check
        postBigDict.append(postDict)
        with open('./postBigDict.json','w', encoding='utf-8') as file:
            file.write(json.dumps(postBigDict, ensure_ascii=False).encode('utf-8').decode())

        posts_processed += 1
        if posts_processed % 10 == 0:
            print(f"{posts_processed} posts processed.")

    if posts_processed % 10 != 0:
        print(f"{posts_processed} posts processed.")

    return postBigDict


def extract(page, numOfPost, infinite_scroll=False, scrape_comment=False):
    option = Options()
    option.add_argument("--disable-infobars")
    option.add_argument("start-maximized")
    option.add_argument("--disable-extensions")

    # Pass the argument 1 to allow and 2 to block
    option.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 1
    })

    # chromedriver should be in the same folder as file
    print("Scrolling through the webpage to load the posts.")
    browser = webdriver.Chrome(executable_path="./chromedriver", options=option)
    _login(browser, EMAIL, PASSWORD)
    browser.get(page)
    lenOfPage = _count_needed_scrolls(browser, infinite_scroll, numOfPost)
    _scroll(browser, infinite_scroll, lenOfPage)

    # click on all the comments to scrape them all!
    # TODO: need to add more support for additional second level comments
    # TODO: ie. comment of a comment

    if scrape_comment:
        print("Scrolling through the webpage and clicking to expose the comments.")
        moreComments = browser.find_elements_by_xpath('//a[@class="_4sxc _42ft"]')
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
            moreComments = browser.find_elements_by_xpath('//a[@class="_4sxc _42ft"]')

    # Now that the page is fully scrolled, grab the source code.
    source_data = browser.page_source

    # Save the source data to disk prior to parsing in case there's an error downstream
    print("Saving the page source to source_data.bin.")
    f = open('source_data.bin','wb')
    pickle.dump(source_data,f)
    f.close()

    postBigDict = parse_html(source_data)
    browser.close()

    return postBigDict


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Facebook Page Scraper")
    required_parser = parser.add_argument_group("required arguments")
    required_parser.add_argument('-page', '-p', help="The Facebook Public Page you want to scrape", required=True)
    required_parser.add_argument('-len', '-l', help="Number of Posts you want to scrape", type=int, required=True)
    optional_parser = parser.add_argument_group("optional arguments")
    optional_parser.add_argument('-infinite', '-i',
                                 help="Scroll until the end of the page (1 = infinite) (Default is 0)", type=int,
                                 default=0)
    optional_parser.add_argument('-usage', '-u', help="What to do with the data: "
                                                      "Print on Screen (PS), "
                                                      "Write to Text File (WT) (Default is WT)", default="CSV")

    optional_parser.add_argument('-comments', '-c', help="Scrape ALL Comments of Posts (y/n) (Default is n). When "
                                                         "enabled for pages where there are a lot of comments it can "
                                                         "take a while", default="No")
    args = parser.parse_args()

    infinite = False
    if args.infinite == 1:
        infinite = True

    scrape_comment = False
    if args.comments == 'y':
        scrape_comment = True

    postBigDict = extract(page=args.page, numOfPost=args.len, infinite_scroll=infinite, scrape_comment=scrape_comment)


    #TODO: rewrite parser
    if args.usage == "WT":
        with open('output.txt', 'w') as file:
            for post in postBigDict:
                file.write(json.dumps(post))  # use json load to recover

    elif args.usage == "CSV":
        with open('data.csv', 'w',) as csvfile:
           writer = csv.writer(csvfile)
           #writer.writerow(['Post', 'Link', 'Image', 'Comments', 'Reaction'])
           writer.writerow(['Post', 'Link', 'Image', 'Comments', 'Shares'])

           for post in postBigDict:
              writer.writerow([post['Post'], post['Link'],post['Image'], post['Comments'], post['Shares']])
              #writer.writerow([post['Post'], post['Link'],post['Image'], post['Comments'], post['Reaction']])

    else:
        for post in postBigDict:
            print("\n")

    print("Finished")

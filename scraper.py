import argparse
import time
import json
import csv
import utils
import re
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains


FB_MOBILE_BASE_URL = 'https://m.facebook.com/'
FB_BASE_URL = 'https://facebook.com/'


with open('facebook_credentials.txt') as file:
    EMAIL = file.readline().split('"')[1]
    PASSWORD = file.readline().split('"')[1]


def _extract_post_text(item):
    # opening paragraph
    actualPosts = item.find_all(
        attrs={"class": "x11i5rnm xat24cr x1mh8g0r x1vvkbs xdj266r x126k92a"})

    # body paragraphs
    actualPosts2 = item.find_all(
        attrs={"class": "x11i5rnm xat24cr x1mh8g0r x1vvkbs xtlvy1s x126k92a"})

    text = ""
    text1 = ""
    if actualPosts:
        for posts in actualPosts:
            paragraphs = posts.find_all("div")
            # print("parag",paragraphs)
            text1 = ""
            for index in range(0, len(paragraphs)):
                text1 += paragraphs[index].text
            #print("text1:", text1)

    text += text1
    if actualPosts2:
        for actualpost2 in actualPosts2:
            #print("acp2", actualPosts2)
            paragraphs = actualpost2.find_all("div")
            #print("parag", paragraphs)
            text1 = ""
            for index in range(0, len(paragraphs)):
                text1 += paragraphs[index].text
            #print("text1:", text1)
            text = text + "\n" + text1

    return text


def _extract_link(item):
    postLinks = item.find_all(
        attrs={"class": "x9f619 x1n2onr6 x1ja2u2z x78zum5 x2lah0s x1qughib x6s0dn4 xozqiw3 x1q0g3np xykv574 xbmpl8g xsag5q8 x1pi30zi x1swvt13 xz9dl7a"})
    link = ""

    for postLink in postLinks:
        pass
        #link = postLink
    return link


def _extract_post_id(item):
    # print("item",item)
    postIds = item.find_all(attrs={"class": "x1i10hfl x1qjc9v5 xjbqb8w xjqpnuy xa49m3k xqeqjp1 x2hbi6w x13fuv20 xu3j5b3 x1q0q8m5 x26u7qi x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xdl72j9 x2lah0s xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r x2lwn1j xeuugli xexx8yu x4uap5 x18d9i69 xkhd6sd x1n2onr6 x16tdsg8 x1hl2dhg xggy1nq x1ja2u2z x1t137rt x1o1ewxj x3x9cwd x1e5q0jg x13rtm0m x1q0g3np x87ps6o x1lku1pv x1a2a7pz x1lliihq x1pdlv7q"})

    post_id = ""
    if len(postIds) == 0:
        postIds = item.find_all(attrs={
            "class": "x1i10hfl x9f619 xe8uvvx x16tdsg8 x1hl2dhg xggy1nq x1o1ewxj x3x9cwd x1e5q0jg x13rtm0m x1n2onr6 x87ps6o x1lku1pv xjbqb8w x76ihet xwmqs3e x112ta8 xxxdfa6 x1ypdohk x1rg5ohu x1qx5ct2 x1k70j0n x1w0mnb xzueoph x1mnrxsn x1iy03kw xexx8yu x4uap5 x18d9i69 xkhd6sd x1o7uuvo x1a2a7pz x1qo4wvw"})

        for postId in postIds:

            if postId.get('href') is not None:

                if re.search(pattern=r'reel/[0-9]+/', string=postId.get('href')) is not None:

                    match = re.search(
                        pattern=r'reel/[0-9]+/', string=postId.get('href')).group(0)
                    post_id = f"https://www.facebook.com/{match.removesuffix('/').removeprefix('reel/')}"

                elif re.search(pattern=r'videos/[0-9]+/', string=postId.get('href')) is not None:

                    match = re.search(
                        pattern=r'videos/[0-9]+/', string=postId.get('href')).group(0)
                    post_id = f"https://www.facebook.com/{match.removesuffix('/').removeprefix('videos/')}"

                elif re.search(pattern=r'/[0-9]+/?', string=postId.get('href')) is not None:

                    match = re.search(
                        pattern=r'/[0-9]+/?', string=postId.get('href')).group(0)
                    post_id = f"https://www.facebook.com/{match.removesuffix('/?').removeprefix('/')}"

    else:

        for postId in postIds:

            if re.search(pattern=r'reel/[0-9]+/', string=postId.get('href')) is not None:
                match = re.search(
                    pattern=r'fbid=[0-9]+&', string=postId.get('href')).group(0)
                post_id = f"https://www.facebook.com/{match.removesuffix('&').removeprefix('fbid=')}"

            elif re.search(pattern=r'/[0-9]+/?', string=postId.get('href')) is not None:

                match = re.search(
                    pattern=r'/[0-9]+/?', string=postId.get('href')).group(0)
                post_id = f"https://www.facebook.com/{match.removesuffix('/?').removeprefix('/')}"

    return post_id


def _extract_image(item):
    postPictures = item.find_all(class_="scaledImageFitWidth img")
    image = ""
    for postPicture in postPictures:
        image = postPicture.get('src')
    return image


def _extract_shares_and_comments(item):
    postShares = item.find_all(
        attrs={"class": "x193iq5w xeuugli x13faqbe x1vvkbs xlh3980 xvmahel x1n0sxbx x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x4zkp8e x3x7a5m x6prxxf xvq8zen xo1l8bm xi81zsa"})
    shares = ""
    comment = ""
    for postShare in postShares:

        x = postShare.string
        if x is not None:
            x = x.split(">", 1)

            if "yorum" in x[0].lower():
                comment = x[0]
            elif "paylaşım" in x[0].lower():
                shares = x[0]
        else:
            shares = "0"
    return [shares.removesuffix(" Paylaşım"), comment.removesuffix(" yorum")]


def _extract_reactions(item):
    postReactions = item.find_all(
        attrs={"class": "xt0b8zv x1jx94hy xrbpyxo xl423tq"})

    reaction = ""
    for postReaction in postReactions:

        x = postReaction.string
        if x is not None:
            x = x.split(">", 1)
            reaction = x[0]
        else:
            reaction = "0"
    return reaction


def _extract_comments(item):
    postComments = item.findAll("div", {"class": "_4eek"})
    comments = dict()
    # print(postDict)
    for comment in postComments:
        if comment.find(class_="_6qw4") is None:
            continue

        commenter = comment.find(class_="_6qw4").text
        comments[commenter] = dict()

        comment_text = comment.find("span", class_="_3l3x")

        if comment_text is not None:
            comments[commenter]["text"] = comment_text.text

        comment_link = comment.find(class_="_ns_")
        if comment_link is not None:
            comments[commenter]["link"] = comment_link.get("href")

        comment_pic = comment.find(class_="_2txe")
        if comment_pic is not None:
            comments[commenter]["image"] = comment_pic.find(
                class_="img").get("src")

        commentList = item.find('ul', {'class': '_7791'})
        if commentList:
            comments = dict()
            comment = commentList.find_all('li')
            if comment:
                for litag in comment:
                    aria = litag.find("div", {"class": "_4eek"})
                    if aria:
                        commenter = aria.find(class_="_6qw4").text
                        comments[commenter] = dict()
                        comment_text = litag.find("span", class_="_3l3x")
                        if comment_text:
                            comments[commenter]["text"] = comment_text.text
                            # print(str(litag)+"\n")

                        comment_link = litag.find(class_="_ns_")
                        if comment_link is not None:
                            comments[commenter]["link"] = comment_link.get(
                                "href")

                        comment_pic = litag.find(class_="_2txe")
                        if comment_pic is not None:
                            comments[commenter]["image"] = comment_pic.find(
                                class_="img").get("src")

                        repliesList = litag.find(class_="_2h2j")
                        if repliesList:
                            reply = repliesList.find_all('li')
                            if reply:
                                comments[commenter]['reply'] = dict()
                                for litag2 in reply:
                                    aria2 = litag2.find(
                                        "div", {"class": "_4efk"})
                                    if aria2:
                                        replier = aria2.find(
                                            class_="_6qw4").text
                                        if replier:
                                            comments[commenter]['reply'][replier] = dict(
                                            )

                                            reply_text = litag2.find(
                                                "span", class_="_3l3x")
                                            if reply_text:
                                                comments[commenter]['reply'][replier][
                                                    "reply_text"] = reply_text.text

                                            r_link = litag2.find(class_="_ns_")
                                            if r_link is not None:
                                                comments[commenter]['reply']["link"] = r_link.get(
                                                    "href")

                                            r_pic = litag2.find(class_="_2txe")
                                            if r_pic is not None:
                                                comments[commenter]['reply']["image"] = r_pic.find(
                                                    class_="img").get("src")
    return comments


def openSeeMore(browser):
    readMore = browser.find_elements(By.XPATH,
                                     "//div[contains(@class,'x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz xt0b8zv xzsf02u x1s688f') and contains(text(), 'Devamını Gör')]")
    if len(readMore) > 0:
        count = 0
        for i in readMore:
            action = ActionChains(browser)
            try:
                action.move_to_element(i).click().perform()
                count += 1
            except:
                try:
                    browser.execute_script("arguments[0].click();", i)
                    count += 1
                except:
                    continue
        if len(readMore) - count > 0:
            print('readMore issue:', len(readMore) - count)
        time.sleep(3)
    else:
        pass


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


def _extract_html(bs_data):

    # Add to check
    with open('./bs.html', "w", encoding="utf-8") as file:
        file.write(str(bs_data.prettify()))

    k = bs_data.find_all(class_="x1n2onr6 x1ja2u2z")
    postBigDict = list()

    for item in k:
        postDict = dict()
        # print(get_page_reviews(item))
        postDict['Post'] = _extract_post_text(item)
        postDict['Link'] = _extract_link(item)
        postDict['PostId'] = _extract_post_id(item)
        postDict['Image'] = _extract_image(item)
        postDict['Shares'] = _extract_shares_and_comments(item)[0]
        postDict['Comments'] = _extract_shares_and_comments(item)[1]
        postDict['Reactions'] = _extract_reactions(item)

        # Add to check
        postBigDict.append(postDict)
        with open('./postBigDict.json', 'w', encoding='utf-8') as file:
            file.write(json.dumps(
                postBigDict, ensure_ascii=False).encode('utf-8').decode())

    return postBigDict


def _login(browser, email, password):
    browser.get("http://facebook.com")
    browser.maximize_window()
    browser.find_element("name", "email").send_keys(email)
    browser.find_element("name", "pass").send_keys(password)

    browser.find_element("name", "login").click()
    time.sleep(3)


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
        time.sleep(3)

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
    browser = webdriver.Chrome(
        executable_path="./chromedriver", options=option)
    _login(browser, EMAIL, PASSWORD)
    browser.get(page)
    lenOfPage = _count_needed_scrolls(browser, infinite_scroll, numOfPost)
    _scroll(browser, infinite_scroll, lenOfPage)

    # click on all the comments to scrape them all!
    # TODO: need to add more support for additional second level comments
    # TODO: ie. comment of a comment

    if scrape_comment:
        # first uncollapse collapsed comments
        unCollapseCommentsButtonsXPath = '//a[contains(@class,"_666h")]'
        unCollapseCommentsButtons = browser.find_elements_by_xpath(
            unCollapseCommentsButtonsXPath)
        for unCollapseComment in unCollapseCommentsButtons:
            action = webdriver.common.action_chains.ActionChains(browser)
            try:
                # move to where the un collapse on is
                action.move_to_element_with_offset(unCollapseComment, 5, 5)
                action.perform()
                unCollapseComment.click()
            except:
                # do nothing right here
                pass

        # second set comment ranking to show all comments
        rankDropdowns = browser.find_elements_by_class_name(
            '_2pln')  # select boxes who have rank dropdowns
        rankXPath = '//div[contains(concat(" ", @class, " "), "uiContextualLayerPositioner") and not(contains(concat(" ", @class, " "), "hidden_elem"))]//div/ul/li/a[@class="_54nc"]/span/span/div[@data-ordering="RANKED_UNFILTERED"]'
        for rankDropdown in rankDropdowns:
            # click to open the filter modal
            action = webdriver.common.action_chains.ActionChains(browser)
            try:
                action.move_to_element_with_offset(rankDropdown, 5, 5)
                action.perform()
                rankDropdown.click()
            except:
                pass

            # if modal is opened filter comments
            ranked_unfiltered = browser.find_elements_by_xpath(
                rankXPath)  # RANKED_UNFILTERED => (All Comments)
            if len(ranked_unfiltered) > 0:
                try:
                    ranked_unfiltered[0].click()
                except:
                    pass

        moreComments = browser.find_elements_by_xpath(
            '//a[@class="_4sxc _42ft"]')
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

            moreComments = browser.find_elements_by_xpath(
                '//a[@class="_4sxc _42ft"]')

    # Now that the page is fully scrolled, grab the source code.

    openSeeMore(browser)
    # elems = browser.find_elements(By.XPATH, "//a[@class='x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g xt0b8zv xo1l8bm']")
    # print(elems)
    # for elem in elems:
    #     attrs = browser.execute_script('var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;',elem)
    #     #print(attrs)

    source_data = browser.page_source

    # Throw your source into BeautifulSoup and start parsing!
    bs_data = bs(source_data, 'html.parser')

    postBigDict = _extract_html(bs_data)
    browser.close()

    return postBigDict


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Facebook Page Scraper")
    required_parser = parser.add_argument_group("required arguments")
    required_parser.add_argument(
        '-page', '-p', help="The Facebook Public Page you want to scrape", required=True)
    required_parser.add_argument(
        '-len', '-l', help="Number of Posts you want to scrape", type=int, required=True)
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

    postBigDict = extract(page=args.page, numOfPost=args.len,
                          infinite_scroll=infinite, scrape_comment=scrape_comment)

    # TODO: rewrite parser
    if args.usage == "WT":
        with open('output.txt', 'w') as file:
            for post in postBigDict:
                file.write(json.dumps(post))  # use json load to recover

    elif args.usage == "CSV":
        with open('data.csv', 'w',) as csvfile:
            writer = csv.writer(csvfile)
            # writer.writerow(['Post', 'Link', 'Image', 'Comments', 'Reaction'])
            writer.writerow(['Post', 'Link', 'Image', 'Comments', 'Shares'])

            for post in postBigDict:
                writer.writerow(
                    [post['Post'], post['Link'], post['Image'], post['Comments'], post['Shares']])
                #writer.writerow([post['Post'], post['Link'],post['Image'], post['Comments'], post['Reaction']])

    else:
        for post in postBigDict:
            print(post)

    print("Finished")

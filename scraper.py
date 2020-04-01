import argparse
import time
import json
import csv

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as bs


def _extract_html(bs_data):

    #Add to check
    with open('./bs.html',"w") as file:
        file.write(str(bs_data.prettify()))

    k = bs_data.find_all(class_="_5pcr userContentWrapper")
    postBigDict = list()

    for item in k:

        # Post Text

        
        actualPosts = item.find_all(attrs={"data-testid": "post_message"})
        

        postDict = dict()
        if actualPosts :
            for posts in actualPosts:
                paragraphs = posts.find_all('p')
                text = ""
                for index in range(0, len(paragraphs)):
                    text += paragraphs[index].text

                postDict['Post'] = text

        else:
            postDict['Post'] = ""

        # Links

        postLinks = item.find_all(class_="_6ks")
        postDict['Link'] = ""
        for postLink in postLinks:
            postDict['Link'] = postLink.find('a').get('href')

        # Images

        postPictures = item.find_all(class_="scaledImageFitWidth img")
        postDict['Image'] = ""
        for postPicture in postPictures:
            postDict['Image'] = postPicture.get('src')

        # Shares
        print("in shares")
        postShares= item.find_all(class_="_4vn1")
        postDict['Shares'] = ""
        for postShare in postShares:
            
            x = postShare.string
            if x is not None:
                x = x.split(">",1)
                print(x)
                postDict['Shares'] = x
            else:
                postDict['Shares'] = "0"

        # Comments

        postComments = item.find_all(attrs={"aria-label" :"Comment"})


        postDict['Comments'] = dict()

        #print(postDict)

        for comment in postComments:

            if comment.find(class_="_6qw4") is None:
                continue

            commenter = comment.find(class_="_6qw4").text
            postDict['Comments'][commenter] = dict()

            comment_text = comment.find("span", class_="_3l3x")

            if comment_text is not None:
                postDict['Comments'][commenter]["text"] = comment_text.text
        
            comment_link = comment.find(class_="_ns_")
            if comment_link is not None:
                postDict['Comments'][commenter]["link"] = comment_link.get("href")

            comment_pic = comment.find(class_="_2txe")
            if comment_pic is not None:
                postDict['Comments'][commenter]["image"] = comment_pic.find(class_="img").get("src")


            commentList = item.find('ul', {'class': '_7791'})
            if commentList:
                postDict['Comments'] = dict()
                comment=commentList.find_all('li')
                if comment:
                    for litag in comment:
                        aria = litag.find(attrs={"aria-label": "Comment"})
                        if aria:
                            commenter = aria.find(class_="_6qw4").text
                            postDict['Comments'][commenter] = dict()
                            comment_text = litag.find("span", class_="_3l3x")
                            if comment_text:
                                postDict['Comments'][commenter]["text"] = comment_text.text
                                #print(str(litag)+"\n")
            
                            comment_link = litag.find(class_="_ns_")
                            if comment_link is not None:
                                postDict['Comments'][commenter]["link"] = comment_link.get("href")

                            comment_pic = litag.find(class_="_2txe")
                            if comment_pic is not None:
                                postDict['Comments'][commenter]["image"] = comment_pic.find(class_="img").get("src")    


                            repliesList=litag.find(class_="_2h2j")
                            if repliesList:
                                reply = repliesList.find_all('li')
                                if reply:
                                    postDict['Comments'][commenter]['reply'] = dict()
                                    for litag2 in reply:
                                        aria2 = litag2.find(attrs={"aria-label": "Comment reply"})
                                        if aria2:
                                            replier = aria2.find(class_="_6qw4").text
                                            if replier:
                                                postDict['Comments'][commenter]['reply'][replier] = dict()
                                                    
                                                reply_text = litag2.find("span", class_="_3l3x")
                                                if reply_text:
                                                    postDict['Comments'][commenter]['reply'][replier][
                                                             "reply_text"] = reply_text.text

                                                r_link = litag2.find(class_="_ns_")
                                                if r_link is not None:
                                                    postDict['Comments'][commenter]['reply']["link"] = r_link.get("href")

                                                r_pic = litag2.find(class_="_2txe")
                                                if r_pic is not None:
                                                    postDict['Comments'][commenter]['reply']["image"] = r_pic.find(class_="img").get("src")




        # # Reactions
        #
        # toolBar = item.find_all(attrs={"role": "toolbar"})
        #
        # if not toolBar:  # pretty fun
        #     continue
        #
        # postDict['Reaction'] = dict()
        #
        # for toolBar_child in toolBar[0].children:
        #
        #     str = toolBar_child['data-testid']
        #     reaction = str.split("UFI2TopReactions/tooltip_")[1]
        #
        #     postDict['Reaction'][reaction] = 0
        #
        #     for toolBar_child_child in toolBar_child.children:
        #
        #         num = toolBar_child_child['aria-label'].split()[0]
        #
        #         # fix weird ',' happening in some reaction values
        #         num = num.replace(',', '.')
        #
        #         if 'K' in num:
        #             realNum = float(num[:-1]) * 1000
        #         else:
        #             realNum = float(num)
        #
        #         postDict['Reaction'][reaction] = realNum

        #Add to check
        postBigDict.append(postDict)
        with open('./postBigDict.txt','w') as file:
            file.write(str(postBigDict))

    return postBigDict


def extract(page, numOfPost, infinite_scroll=False, scrape_comment=False):
    with open('./facebook_credentials.txt') as file:
        email = file.readline().split('"')[1]
        password = file.readline().split('"')[1]

    option = Options()

    option.add_argument("--disable-infobars")
    option.add_argument("start-maximized")
    option.add_argument("--disable-extensions")

    # Pass the argument 1 to allow and 2 to block
    option.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 1
    })

    browser = webdriver.Chrome(executable_path="/usr/local/bin/chromedriver", options=option)
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

    if scrape_comment:

        moreComments = browser.find_elements_by_xpath('//a[@class="_4sxc _42ft"]')
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

            moreComments = browser.find_elements_by_xpath('//a[@class="_4sxc _42ft"]')

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

import dlt, json, os, time, requests
import pandas as pd
import undetected_chromedriver as uc
from datetime import datetime, timedelta, timezone
from dlt.common import pendulum
from dlt.destinations import filesystem
from dlt.sources.helpers.rest_client import RESTClient
from dlt.sources.helpers.rest_client.auth import BearerTokenAuth
from dlt.sources.helpers.rest_client.paginators import JSONLinkPaginator
from pytz import utc
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from tqdm.notebook import tqdm
from webdriver_manager.chrome import ChromeDriverManager


class reddit_scrapper(object):
    def __init__(self, headless=True, no_sandbox=True, disable_dev_shm_usage=True, days_extracted=3):
        # Setup Chrome driver
        options = webdriver.ChromeOptions()
        # set chromedriver attributes
        if headless:
            options.add_argument("--headless")  # uncomment to run silently
        if no_sandbox:
            options.add_argument("--no-sandbox")
        if disable_dev_shm_usage:
            options.add_argument("--disable-dev-shm-usage")
        #Download the chromedriver if not available and initiate an instance of chromedriver
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        #initiate the posts
        self.posts_extracted = []
        #initiate the comments
        self.comments_extracted = []
        #initiate the days_extracted
        self.days_extracted = days_extracted
        

    def get_posts(self):
        # Go to Reddit search
        self.driver.get("https://www.reddit.com/search/?q=bitcoin")
        time.sleep(5)

        # Optional: interact with dropdown menu to select time filter
        try:
            dropdown_menu = self.driver.find_element(By.XPATH, '//*[@id="search_modifier_time_range"]')
            dropdown_menu.click()
            time.sleep(2)
            selection = self.driver.find_element(By.XPATH, '//*[@id="search_modifier_time_range"]/div/search-telemetry-tracker[4]/li/a')
            selection.click()
            time.sleep(5)
        except Exception as e:
            print("Dropdown interaction failed:", e)

        # Scroll to load more posts
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scroll_count = 0

        #set the number of times to repeat scroll action on browser
        MAX_SCROLLS = 100  # tune as needed

        #execute scrolling down
        while scroll_count < MAX_SCROLLS:
            self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
            time.sleep(3)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            scroll_count += 1
        
        # Extract post links
        post_elements = self.driver.find_elements(By.XPATH, '//*[@id="main-content"]/div/search-telemetry-tracker')
        comments_post = []
        post_id = 1
        # list to store posts extracted
        data = []
        for post in tqdm(post_elements):
            title = post.find_element(By.TAG_NAME, "a").text
            post_url = post.find_element(By.TAG_NAME, "a").get_attribute("href")
            time_str = post.find_element(By.TAG_NAME, "time").get_attribute("datetime")
            numerics = post.find_elements(By.TAG_NAME, 'faceplate-number')
            posted_time = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S.%fZ")
            # append the post
            data.append({'post_id': post_id,\
                          'post_title': title,\
                          'post_timestamp': posted_time,\
                          'post_url': post_url})
            #increment the post_id
            post_id+=1
        #set the attribute posts_extracted
        self.posts_extracted = data
        
    def get_comments(self):
        #filter to posts within last 3 days
        posts = list(filter(lambda post: post['post_timestamp']>=datetime.now()-timedelta(days=self.days_extracted), self.posts_extracted))
        #used to only store the comments of the posts extracted
        comments = []
        
        #iterate through the posts
        for post in tqdm(posts):
            post_id = post['post_id']
            post_title = post['post_title']
            post_timestamp = post['post_timestamp']
            post_url = post['post_url']
            
            # Go to Reddit search
            self.driver.get(post_url)
            time.sleep(2)
            
            #get the reddit post_body
            post_body = self.driver.find_element(By.TAG_NAME, 'shreddit-post')
            try:
                post_content = post_body.find_element(By.CSS_SELECTOR, '#t3_1gk9scx-post-rtjson-content').text
            except:
                post_content = ""
        
            #get the reddit post image content if any
            try:
                post_img_url = post_body.find_element(By.CSS_SELECTOR, '#post-image').get_attribute("src")
            except:
                post_img_url = ""
        
            # Scroll to load more posts
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_count = 0
            MAX_SCROLLS = 300  # tune as needed
        
            #scroll down the page to get all the commments
            while scroll_count < MAX_SCROLLS:
                self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
                time.sleep(3)
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                time.sleep(1)
                try:
                    view_more_comments = self.driver.find_element(By.CSS_SELECTOR, "#comment-tree > faceplate-partial > div:nth-child(2) > faceplate-tracker")
                    view_more_comments.click()
                except:
                    break
                time.sleep(1)
                scroll_count += 1
        
            #scroll to the top of the page
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
        
            #extract the comments on post
            comment_tree = self.driver.find_element(By.CSS_SELECTOR, '#comment-tree > shreddit-comment:nth-child(3)')
            post_comments =  self.driver.find_elements(By.TAG_NAME, 'shreddit-comment')
        
            comment_id = 1
            #comment-tree > faceplate-partial > div:nth-child(2) > faceplate-tracker > button
            for post_comment in tqdm(post_comments):
                comment_date = post_comment.find_element(By.TAG_NAME, 'time').get_attribute('datetime')
                comment_list = list(filter(lambda x: len(x)>15, post_comment.text.split('\n')))
                comment_text = '\n'.join(comment_list)
                comment = {'post_id':post_id,\
                           'post_title':post_title,\
                           'post_timestamp': post_timestamp,\
                           'post_url':post_url,\
                           'comment_id':comment_id,\
                           'comment_date': datetime.strptime(comment_date, "%Y-%m-%dT%H:%M:%S.%fZ"),\
                           'comment_text':comment_text}
                self.comments_extracted.append(comment)
                yield comment

    def close(self):
        self.driver.quit()






class cryptopanic_api_scrapper(object):
    def __init__(self, headless=True, no_sandbox=True, disable_dev_shm_usage=True, days_extracted=3):
            
        #set options
        self.headless = headless
        self.no_sandbox = no_sandbox
        self.disable_dev_shm_usage = disable_dev_shm_usage
        self.days_extracted = days_extracted
        
        #initiate the posts
        self.posts_extracted = []
        #initiate the comments
        self.comments_extracted = []
        #initiate the days_extracted
        self.days_extracted = days_extracted
        #initiate the base url
        self.base_url = "https://cryptopanic.com/api/v1/posts/"

    def fetch_cryptopanic_feed(self):
        API_URL = self.base_url
        AUTH_TOKEN = dlt.secrets['cryptopanic_api_key']['token']
        
        params = {
            "auth_token": AUTH_TOKEN,
            "currencies": dlt.config['cryptopanic-headers']['currencies'],
            "public": dlt.config['cryptopanic-headers']['public'],
            "filter": dlt.config['cryptopanic-headers']['filter']
        }
    
        next_url = API_URL

        while next_url:
            print(next_url)
            res = requests.get(next_url, params=params if next_url == API_URL else None)
            data = res.json()
            post_id = 1
            for post in data.get("results", []):
                title = post.get("title", "").strip()
                published_at = datetime.fromisoformat(post.get("published_at","").replace("Z", ""))
                url = post.get("url")
                self.posts_extracted.append([post_id, title, published_at, url])
    
            # Handle pagination
            next_url = data['next']
        
        results_df = pd.DataFrame(self.posts_extracted, columns=['post_id', 'post_title', 'post_timestamp', 'post_url'])
        results_df['post_timestamp'] = pd.to_datetime(results_df['post_timestamp'], utc=True)
        results_df = results_df.loc[results_df.post_timestamp>datetime.now(timezone.utc)-timedelta(days=self.days_extracted)]
        self.posts_extracted = results_df.values

    def get_comments(self):
        
        #create an array to store the comments of the post        
        comment_objects = set()

        #loop through the post
        for post_id, title, published_at, url in tqdm(self.posts_extracted):
            # Setup undetected Chrome driver
            options = uc.ChromeOptions()
            
            # set chromedriver attributes
            if self.headless:
                options.add_argument("--headless")  # uncomment to run silently
            if self.no_sandbox:
                options.add_argument("--no-sandbox")
            if self.disable_dev_shm_usage:
                options.add_argument("--disable-dev-shm-usage")
            #Download the chromedriver if not available and initiate an instance of chromedriver
            driver = uc.Chrome(service=Service(ChromeDriverManager().install()), options=options)

            # Navigate to the CryptoPanic article
            driver.get(url)
            time.sleep(3)

            #maximize the window resolution
            driver.set_window_size(1920, 1080)
    
            try:
                # Click "Accept" button if present
                try:
                    accept_btn = driver.find_element(By.XPATH, "/html/body/div[1]/div[4]/div/div[3]/a")
                    time.sleep(2)
                    accept_btn.click()
                    time.sleep(2)
                except:
                    pass  # Accept button may not always appear
        
                last_scroll = -1
                scrolls = 0
        
                comment_idx = 0
                comment_len = len(driver.find_elements(By.CLASS_NAME, "comment-content"))
        
                while comment_idx < comment_len:
                    # Comments live inside this block
                    comment_blocks = driver.find_element(By.CSS_SELECTOR, "#detail_pane > div:nth-child(7) > div.comments-list")
                    comment_blocks.click()
                    
                    # Extract visible comments
                    comments = driver.find_elements(By.CLASS_NAME, "comment-content")
                    last_comment = ''
            
                    comment = comments[comment_idx]
                    comment_body = comment.find_element(By.CLASS_NAME, "comment-body")
                    comment_timestamp = comment.find_element(By.TAG_NAME, 'time').get_attribute('datetime')
                    text = comment.text.strip()
                    cleaned = comment_timestamp.split(' (')[0]  # 'Mon Apr 07 2025 21:57:06 GMT+0800'

                    comment_object = {'post_id':post_id,\
                               'post_title':title,\
                               'post_timestamp': published_at,\
                               'post_url':url,\
                               'comment_id':comment_idx,\
                               'comment_date': datetime.strptime(cleaned, "%a %b %d %Y %H:%M:%S GMT%z"),\
                               'comment_text':text}
                    
                    comment_idx+=1
                    scrolls+=1
                    ActionChains(driver).move_to_element(comment).perform()        
                    
                    # Final output
                    if comment_object not in comment_objects:
                        comment_objects.add(comment_object)
                        print(len(comment_objects))
                        yield comment
        
            except Exception as e:
                print("❌ Error extracting comments:", e)

            self.comments_extracted = list(comment_objects)
            driver.close()



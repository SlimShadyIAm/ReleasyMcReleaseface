import feedparser
import time
def main():
    feed = "https://developer.apple.com/news/releases/rss/releases.rss"
    data_old = feedparser.parse(feed)
    
    time.sleep(10)
    while True:
        data = feedparser.parse(feed)
        # has the feed changed?
        # print(data.status)
        # get newest post date from cached data. any new post will have a date newer than this
        max_prev_date = max([something["published_parsed"] for something in data_old.entries])
        # get new posts
        new_posts = [post for post in data.entries if post["published_parsed"] > max_prev_date]
        # if there rae new posts
        if (len(new_posts) > 0):
            # check thier tags
            for post in new_posts:
                print(f'NEW GOOD ENTRY: {post.title} {post.link}')
            # await self.check_new_entries(feed, new_posts)  
    
        data_old = data
        time.sleep(10)

if __name__ == "__main__":
    main()
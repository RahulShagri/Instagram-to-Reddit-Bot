import praw
from praw.models import InlineImage
from instaloader import *
import datetime
import shutil
import os
import time as sleep_time


script_path = os.path.abspath(os.path.dirname(__file__))
folder_path = script_path + "/ManipalUpdatesLatest"

L = instaloader.Instaloader()

while True:
    try:
        clear = lambda: os.system('cls')

        for second in reversed(range(15)):
            clear()

            print(f"Time until next sync: {second}s")
            sleep_time.sleep(1)

        #Check latest reddit post

        posted_database_file = open(script_path + "/posted_database.txt", "r")
        posted_files = posted_database_file.read().split(", ")
        latest_reddit_post = posted_files[-1]

        print(f"Latest post on reddit is {latest_reddit_post}")

        posted_database_file.close()

        #check new instagram posts

        profile = Profile.from_username(L.context, 'manipalupdates')

        new_posts = []

        for post in profile.get_posts():

            if post.shortcode == latest_reddit_post:
                break
            else:
                new_posts.append(post.shortcode)

        if len(new_posts) == 0:
            print("No new posts found.")
            sleep_time.sleep(1.5)
            continue

        print(f"\nFound {len(new_posts)} new posts on instagram.")
        print(f"New posts on instagram : {new_posts}")
        print("Initiating an update...\n")

        if not os.path.exists(folder_path):
            os.mkdir(folder_path)

        L.login(<Your instagram user ID>, <Your instagram password>)

        shortcode = new_posts[-1]

        post = Post.from_shortcode(L.context, shortcode)
        print("Downloading files...")
        L.download_post(post, target='ManipalUpdatesLatest')
        print("Download successful!")

        time_posted = str(post.date)
        file_name = time_posted.replace(":", "-").replace(" ", "_")
        file_name += "_UTC"

        date = time_posted[:10].split("-")
        year_posted = int(date[0])
        month_posted = int(date[1])
        day_posted = int(date[2])

        local_time = str(post.date_local)
        time = local_time[11:].split(":")
        hour_posted = int(time[0])
        minute_posted = int(time[1])
        second_posted = int(time[2])

        x = datetime.datetime(year_posted, month_posted, day_posted, hour_posted, minute_posted, second_posted)

        date_posted = x.strftime("%d/%b/%Y, %H:%M:%S IST")

        try:
            title_file = open(f"{folder_path}/{file_name}.txt", "r")
            title = title_file.read()
            title_file.close()
        except:
            title = ''

        reddit_post_title = f"[Manipal Updates: {date_posted}] {title}"

        if len(reddit_post_title) > 300:
            reddit_post_title = reddit_post_title[:297] + "..."

        print(f"\nReddit post title will be: {reddit_post_title}\n")

        reddit = praw.Reddit(client_id=<Your client id>,
                             client_secret=<Your client secret>,
                             username=<Your reddit username>,
                             password=<Your reddit password>,
                             user_agent=<Your user agent>)

        subreddit = reddit.subreddit("manipal")

        media_count = post.mediacount

        post_object = None

        if media_count == 1:
            image_file_name = file_name

            if os.path.isfile(f"{folder_path}/{image_file_name}.mp4"):
                post_object = subreddit.submit_video(reddit_post_title, f"{folder_path}/{image_file_name}.mp4", thumbnail_path=f"{folder_path}/{image_file_name}.jpg")
            else:
                post_object = subreddit.submit_image(reddit_post_title, f"{folder_path}/{image_file_name}.jpg")

        elif media_count>1:
            images = []
            image_file_name = file_name
            for image_number in range(1, media_count+1):
                images.append({"image_path": f"{folder_path}/{image_file_name}_{image_number}.jpg"})

            post_object = subreddit.submit_gallery(reddit_post_title, images)

        post_object.reply(f"This is an automated cross-post from the [Manipal Updates Instagram Page](https://www.instagram.com/manipalupdates/)."
                          f"\n\nYou can find the original instagram post here: [Manipal Updates Instagram Page's Latest Post](https://www.instagram.com/p/{shortcode}/)"
                          f"\n\nIf you have any questions or suggestions, please feel free to contact the developer, u/fruehmittel.")

        post_object.mod.distinguish(sticky=True)

        print("\nNew post has been cross-posted to r/Manipal")

        posted_database_file = open(script_path + "/posted_database.txt", "a")
        posted_database_file.write(", " + shortcode)
        posted_database_file.close()

        print("posted_database file has been updated!")
        sleep_time.sleep(1.5)

        shutil.rmtree(folder_path)

    except:
        print("An error occurred. We are trying again.")
        sleep_time.sleep(1.5)
        continue
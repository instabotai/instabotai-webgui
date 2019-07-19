import os
from flask import Flask, render_template
from instabot import Bot
import argparse
import time

parser = argparse.ArgumentParser(add_help=True)
parser.add_argument('-u', type=str, help="username")
parser.add_argument('-p', type=str, help="password")
parser.add_argument('-proxy', type=str, help="proxy")
args = parser.parse_args()


app = Flask(__name__)

bot = Bot()

bot.login(username=args.u, password=args.p, proxy=args.proxy)

bot.api.get_self_username_info()

username = str(args.u)
profile_pic = bot.api.last_json["user"]["profile_pic_url"]
followers = bot.api.last_json["user"]["follower_count"]
following = bot.api.last_json["user"]["following_count"]
media_count = bot.api.last_json["user"]["media_count"]

@app.route("/")
def index():
    return render_template("index.html", username=username,
                           profile_pic=profile_pic, followers=followers,
                           following=following, media_count=media_count);

@app.route("/like_self_media_comments")
def like_self_media_comments():
    x = 0
    y = 0
    while True:
        try:
            bot.api.get_total_self_user_feed(min_timestamp=None)
            item = bot.api.last_json["items"][x]["caption"]["media_id"]
            bot.like_media_comments(item)
            print("sleeping for 120 seconds")
            time.sleep(120)
            x += 1
            y = 0
            print("Like comments on next picture")
        except:
            time.sleep(120)
            print("Like comments on next picture")
            x += 1
            if y == 4:
                x = 0
    return render_template("index.html", username=username,
                       profile_pic=profile_pic, followers=followers,
                       following=following, media_count=media_count);

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)

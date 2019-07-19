import os
from flask import Flask, render_template
from instabot import Bot
import argparse

parser = argparse.ArgumentParser(add_help=True)
parser.add_argument('-u', type=str, help="username")
parser.add_argument('-p', type=str, help="password")
parser.add_argument('-proxy', type=str, help="proxy")
args = parser.parse_args()

bot = Bot()

bot.login(username=args.u, password=args.p, proxy=args.proxy)



app = Flask(__name__)

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


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)

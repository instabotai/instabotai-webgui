import os
from flask import Flask, render_template, request
from instabot import Bot
import argparse
import time
import threading
import random
import sys

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

@app.route("/like_comments")
def like_comments():
    return render_template("like_comments.html", username=username,
                           profile_pic=profile_pic, followers=followers,
                           following=following, media_count=media_count);

@app.route("/watch_infinity_stories")
def watch_infinity_stories():
    return render_template("watch_infinity_stories.html", username=username,
                           profile_pic=profile_pic, followers=followers,
                           following=following, media_count=media_count);

@app.route("/multibot")
def multibots():
    return render_template("multibot.html", username=username,
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
    return render_template("like_self_media_comments.html", username=username,
                       profile_pic=profile_pic, followers=followers,
                       following=following, media_count=media_count);


@app.route("/watch_stories", methods=['GET', 'POST'])
def watch_all_stories():
    watch_username = request.form['watch_username']
    if len(sys.argv) >= 10:
        bot.logger.info(
            """
                Going to get '%s' likers and watch their stories (and stories of their likers too).
            """ % (sys.argv[1])
        )
        user_to_get_likers_of = bot.convert_to_user_id(sys.argv[1])
    else:
        bot.logger.info(
            """
                Going to get """ + watch_username + """ likers and watch their stories (and stories of their likers too).
                You can specify username of another user to start (by default we use you as a starting point).
            """
        )
        user_to_get_likers_of = bot.get_user_id_from_username(watch_username)
    
    current_user_id = user_to_get_likers_of
    while True:
        try:
            # GET USER FEED
            if not bot.api.get_user_feed(current_user_id):
                print("Can't get feed of user_id=%s" % current_user_id)

            # GET MEDIA LIKERS
            user_media = random.choice(bot.api.last_json["items"])
            if not bot.api.get_media_likers(media_id=user_media["pk"]):
                bot.logger.info(
                    "Can't get media likers of media_id='%s' by user_id='%s'" % (user_media["pk"], current_user_id)
                )

            likers = bot.api.last_json["users"]
            liker_ids = [
                str(u["pk"]) for u in likers if not u["is_private"] and "latest_reel_media" in u
            ][:20]

            # WATCH USERS STORIES
            if bot.watch_users_reels(liker_ids):
                bot.logger.info("Total stories viewed: %d" % bot.total["stories_viewed"])

            # CHOOSE RANDOM LIKER TO GRAB HIS LIKERS AND REPEAT
            current_user_id = random.choice(liker_ids)

            if random.random() < 0.05:
                current_user_id = user_to_get_likers_of
                bot.logger.info("Sleeping and returning back to original user_id=%s" % current_user_id)
                time.sleep(90 * random.random() + 60)

        except Exception as e:
            # If something went wrong - sleep long and start again
            bot.logger.info(e)
            current_user_id = user_to_get_likers_of
            time.sleep(240 * random.random() + 60)

@app.route("/start_multibot")
def multibot():
    def reply_pending_messages():
        reply_pending = 0
        while True:
            try:
                bot.api.get_pending_inbox()
                for w in bot.api.last_json["inbox"]["threads"]:
                    thread_id = w["thread_id"]
                    username = w["users"][0]["username"]
                    full_name = w["users"][0]["full_name"]
                    userid = bot.get_user_id_from_username(username)
                    reply_pending += 1
                    print("Reply pending message " + thread_id)
                    print("Replied Pending messages: " + str(reply_pending))
                    bot.api.approve_pending_thread(thread_id)
                    bot.send_message("Thanks " +str(full_name) +  ", please comment and like all my pictures also follow me", userid, thread_id=thread_id)
                    time.sleep(60)
            except:
                time.sleep(160)
                pass


    def watch_stories():
        if len(sys.argv) >= 10:
            bot.logger.info(
                """
                    Going to get '%s' likers and watch their stories
                    (and stories of their likers too).
                """ % (sys.argv[1])
            )
            user_to_get_likers_of = bot.convert_to_user_id(sys.argv[1])
        else:
            bot.logger.info(
                """
                    Going to get your likers and watch their stories
                    (and stories of their likers too).
                    You can specify username of another user to start
                    (by default we use you as a starting point).
                """
            )
            user_to_get_likers_of = bot.get_user_id_from_username(args.u)

        current_user_id = user_to_get_likers_of
        total_stories = 0
        error_sleep = 0
        error_sleeps = 0

        while True:
            try:
                # GET USER FEED
                if not bot.api.get_user_feed(current_user_id):
                    print("Can't get feed of user_id=%s" % current_user_id)

                # GET MEDIA LIKERS
                user_media = random.choice(bot.api.last_json["items"])
                if not bot.api.get_media_likers(media_id=user_media["pk"]):
                    print(
                        "Can't get media likers of media_id='%s' by user_id='%s'"
                        % (user_media["pk"], current_user_id)
                    )
                likers = bot.api.last_json["users"]
                liker_ids = [
                    str(u["pk"]) for u in likers if not u["is_private"] and "latest_reel_media" in u
                ][:20]

                # WATCH USERS STORIES
                if bot.watch_users_reels(liker_ids):
                    bot.logger.info("Total stories viewed: %d" % bot.total["stories_viewed"])
                    error_sleep = 0
                    error_sleeps = 0
                    if bot.total["stories_viewed"] > 1900:
                        total_stories += 2000
                        print("Total stories watched " + str(total_stories))
                        bot.total["stories_viewed"] = 0
                        print("sleeping for 310 sec")
                        time.sleep(310 + random.random())

            # CHOOSE RANDOM LIKER TO GRAB HIS LIKERS AND REPEAT
                current_user_id = random.choice(liker_ids)
                if random.random() < 0.05:
                    current_user_id = user_to_get_likers_of
                    bot.logger.info("Sleeping and returning back to original user_id=%s"% current_user_id)
                    time.sleep(3 * random.random() + 1)
                    error_sleep += 1
                    if error_sleep == 4:
                        print("sleeping for 1780 seconds")
                        time.sleep(1780 + random.random())

            except Exception as e:
                # If something went wrong - sleep long and start again
                bot.logger.info(e)
                error_sleeps += 1
                if error_sleeps == 4:
                    print("sleeping for 1780 seconds")
                    time.sleep(1780 + random.random())

                current_user_id = user_to_get_likers_of
                time.sleep(5 * random.random() + 5)



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


    thread1 = threading.Timer(7.0, watch_stories)
    thread2 = threading.Timer(13.0, reply_pending_messages)
    thread3 = threading.Timer(2.0, like_self_media_comments)
    thread1.start()
    thread2.start()
    thread3.start()
    return render_template("index.html", username=username,
                       profile_pic=profile_pic, followers=followers,
                       following=following, media_count=media_count);

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8000, debug=True)


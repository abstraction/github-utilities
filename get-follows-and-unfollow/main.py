from itertools import count
import os
from math import ceil
import requests
from dotenv import dotenv_values
from PyOrgMode import PyOrgMode

config = dotenv_values(".env")  # config = {"USER": "foo", "EMAIL": "foo@example.org"}
api_url = "https://api.github.com"
starred_url = f"{api_url}/users/abstraction/starred"  # {/owner}{/repo}
# ?per_page=100&page=

headers = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": f'token {config["GITHUB_TOKEN"]}',
}


def get_user_details(user):
    print(f"Getting details of: {user}")
    res = requests.get(f"{api_url}/users/{user}", headers=headers)
    if res.status_code == 200:
        return res.json()
    else:
        raise Exception(f"Error getting user detail of user {user}")


def get_following(following_count):
    pages = ceil(following_count / 100)
    users = []
    for page in range(1, pages + 1):
        res = requests.get(
            f"{api_url}/users/abstraction/following?per_page=100&page={page}",
            headers=headers,
        )
        if res.status_code == 200:
            data = res.json()
            for user in data:
                user_info = get_user_details(user["login"])
                users.append(
                    {
                        "username": user["login"],
                        "profile_url": user_info["html_url"],
                        "followers": user_info["followers"],
                        "blog": user_info["blog"] if user_info["blog"] else None,
                        "bio": user_info["bio"] if user_info["bio"] else None,
                    }
                )
    return users


def unfollow_user(user):
    res = requests.delete(f"{api_url}/user/following/{user}", headers=headers)
    if res.status_code == 204:
        return True
    else:
        return False


def save_following_to_org(data):
    base = PyOrgMode.OrgDataStructure()
    base.load_from_file(
        os.path.normpath(os.path.join(os.getcwd(), "dist/following.org"))
    )
    h1 = PyOrgMode.OrgNode.Element()
    h1.level = 1
    h1.heading = data["username"] + " " + data["profile_url"]
    h1.append(f"Followers: {data['followers']}\n")
    h1.append(f"Blog: {data['blog']}\n")
    h2_bio = PyOrgMode.OrgNode.Element()
    h2_bio.level = 2
    h2_bio.heading = "Bio"
    h2_bio.append(f"{data['bio']}\n")
    h2_notes = PyOrgMode.OrgNode.Element()
    h2_notes.level = 2
    h2_notes.heading = "Comments"
    h2_notes.append(f"None\n\n")
    h1.append_clean(h2_bio)
    h1.append_clean(h2_notes)
    base.root.append_clean(h1)
    base.save_to_file(os.path.normpath(os.path.join(os.getcwd(), "dist/following.org")))
    return True


# https://api.github.com/users/abstraction/following

# TODO Breakdown main?
if __name__ == "__main__":
    print("Starting...")
    my = get_user_details("abstraction")
    to_unfollow = my["following"]
    count_unfollow = 0
    print(f"You currently follow {to_unfollow} people")
    # Creating log.org
    with open(
        os.path.normpath(os.path.join(os.getcwd(), "dist/following.org")), "a"
    ) as file:
        file.write("#+TITLE: My Github Following")
        file.write("\n\n")  # impt otherwise PyOrgMode start on same line
    pages = ceil(to_unfollow / 100)
    users = []
    for page in range(pages):
        res = requests.get(
            f"{api_url}/users/abstraction/following?per_page=100&page={page + 1}",
            headers=headers,
        )
        if res.status_code == 200:
            data = res.json()
            for user in data:
                count_unfollow += 1
                user_info = get_user_details(user["login"])
                is_save = save_following_to_org(
                    {
                        "username": user["login"],
                        "profile_url": user_info["html_url"],
                        "followers": user_info["followers"],
                        "blog": user_info["blog"] if user_info["blog"] else None,
                        "bio": user_info["bio"] if user_info["bio"] else None,
                    }
                )
                is_unfollowed = unfollow_user(user["login"])
                if is_save and is_unfollowed:
                    print(
                        f"✅ [{count_unfollow}/{to_unfollow}] {user['login']} is saved & unfollowed."
                    )
                    with open(
                        os.path.normpath(
                            os.path.join(
                                os.getcwd(), "get-follows-and-unfollow/log.org"
                            )
                        ),
                        "a",
                    ) as file:
                        file.write(f"✅ {user['login']} is saved & unfollowed.\n")
                else:
                    print(f"❌ {user['login']} error.")
                    with open(
                        os.path.normpath(
                            os.path.join(
                                os.getcwd(), "get-follows-and-unfollow/log.org"
                            )
                        ),
                        "a",
                    ) as file:
                        file.write(
                            f"❌ [{count_unfollow}/{to_unfollow}] {user['login']} error.\n"
                        )

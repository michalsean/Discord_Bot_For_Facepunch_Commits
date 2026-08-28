import discord
import asyncio
import json
import re
import aiohttp
import os

TOKEN = "Put Discord Token IN"
CHANNEL_ID = "#Put Channel Token Here"
BASE_URL = "https://commits.facepunch.com/r/rust_reboot/main?format=json"
CHECK_INTERVAL = 60

intents = discord.Intents.default()
client = discord.Client(intents=intents)


def clean_text(text):
    if not text:
        return "No description"
    text = text.encode("utf-8", "ignore").decode("utf-8", "ignore")
    text = re.sub(r"[^\x20-\x7E\n\r\t]", "", text)
    return text.strip()


async def fetch_commits():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(BASE_URL, timeout=15) as r:
                if r.status != 200:
                    print("HTTP error:", r.status)
                    return []

                data = await r.json()

        if "results" not in data:
            print("Bad JSON format")
            return []

        commits = []

        for item in data["results"]:
            author_data = item.get("author")

            author_name = ""
            avatar = None

            if isinstance(author_data, dict):
                author_name = (
                    author_data.get("name")
                    or author_data.get("username")
                    or author_data.get("display_name")
                    or "Unknown"
                )
                avatar = author_data.get("avatar")
            elif isinstance(author_data, str):
                author_name = author_data

            commits.append({
                "id": str(item.get("id")),
                "author": author_name,
                "avatar": avatar,
                "message": clean_text(item.get("message")),
                "branch": item.get("branch", "main"),
                "url": f"https://commits.facepunch.com/{item.get('id')}"
            })

        print(f"Fetched {len(commits)} commits")
        return commits

    except Exception as e:
        print("Fetch error:", e)
        return []


def load_last():
    try:
        with open("last.json", "r") as f:
            data = json.load(f)
            print("Loaded last:", data.get("id"))
            return data.get("id")
    except:
        return None


def save_last(commit_id):
    try:
        with open("last.json", "w") as f:
            json.dump({"id": commit_id}, f)
        print("Saved last:", commit_id)
    except Exception as e:
        print("Save error:", e)


async def send_commit(channel, commit):
    message = commit["message"] or "No description"

    formatted = "\n".join(
        f"+ {line}" for line in message.split("\n") if line.strip()
    )

    embed = discord.Embed(
        title=f"Commit {commit['id']}",
        url=commit["url"],
        description=f"```diff\n{formatted[:800]}\n```" if formatted else "No changes listed",
        color=0x161b22
    )

    if commit["avatar"]:
        embed.set_author(name=commit["author"], icon_url=commit["avatar"])
    else:
        embed.set_author(name=commit["author"])

    embed.add_field(name="Branch", value=f"`{commit['branch']}`", inline=True)
    embed.add_field(name="Changeset", value=f"`{commit['id']}`", inline=True)
    embed.add_field(name="Repo", value="`rust_reboot`", inline=True)

    embed.set_footer(text="commits.facepunch.com (made by frogboots123)")

    await channel.send(embed=embed)


async def check_loop():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    if not channel:
        print("Channel not found")
        return

    print("Running in:", os.getcwd())

    while True:
        commits = await fetch_commits()

        if not commits:
            await asyncio.sleep(CHECK_INTERVAL)
            continue

        print("Top commit:", commits[0]["id"])

        last_saved = load_last()

        if last_saved is None:
            print("First run, posting recent commits")

            for commit in reversed(commits[:5]):
                await send_commit(channel, commit)

            save_last(commits[0]["id"])
            await asyncio.sleep(CHECK_INTERVAL)
            continue

        new_commits = []

        for commit in commits:
            if commit["id"] == last_saved:
                break
            new_commits.append(commit)

        if new_commits:
            print(f"Posting {len(new_commits)} new commits")

            for commit in reversed(new_commits):
                await send_commit(channel, commit)

            # critical fix for duplicates
            save_last(new_commits[0]["id"])

        await asyncio.sleep(CHECK_INTERVAL)


@client.event
async def on_ready():
    print("Bot online as", client.user)
    asyncio.create_task(check_loop())


client.run(TOKEN)
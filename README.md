# Releasy McReleaseface

---

## What is this?

A Discord bot which watches Apple's [release feed](https://developer.apple.com/news/releases/rss/releases.rss) for new updates to iOS, iPadOS, macOS, watchOS and tvOS.

Server managers have the ability to subscribe to updates from a device and choose a channel for updates to be posted to. Additionally, you can set a role to ping for each OS type, when an update is posted.

## How to install

You'll need `pipenv` to get started.

1.  `git clone https://github.com/SlimShadyIAm/ReleasyMcReleaseface && cd ReleasyMcReleaseface`
2.  `pipenv install --python 3.8.3`
3.  `pipenv shell`
4.  Set up your Discord bot token as an environment variable called `IOS_TOKEN`
5.  `python main.py`

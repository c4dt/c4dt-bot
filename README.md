# C4DT Bot

Here comes the C4DT Matrix bot using agentic LLMs to answer all questions about
life, the universe, and everything!
Its main goal is to propose articles for weekly picks.
But it can also be used as a generic LLM, with one big downside:
it doesn't keep track of previous messages - every message is new!

## TLDR

Creating a number of weekly picks:

```text
4 weekly picks on Switzerland
```

Updating your personal preferences:

```text
I really like to dive into the policy of digital trust related documents between
governments.
Nothing better than to read some description of what's happening in the law, and how
to define working together in the digital realm.
```

Modifying urls:

```text
Please add the following URL when looking for news: https://slashdot.org
```

Generic queries:

```text
Please tell a joke about an IT guy learning policy.
```

## Commands

The following commands are available:

- HELP - no arguments
- PERSONAL_INTEREST - the new personal interest description the user gives
- WEEKLY - 1st mandatory argument is the number of weekly picks the user wants - per default it's 3 picks. Optional 2nd argument is specifications of subject in weekly picks
- WEEKLY_URLS - a list of URLs for the weekly picks
- GENERAL - the question the user wants the bot to answer

However, the bot tries to infer the command from what you write, so there
is no need to give the command in clear.

## Storage

For every user, the bot stores the following:

- personal interests - updated from the queries, and can also be updated directly by the user.
This is used for searching relevant articles from the news sites
- news site urls - per default, three URLs are defined. But you can add/remove/modify as you wish

## Flow of the agents

The flow is given in `agent.py::answer_message`:

```python
cmd = await get_command(user, message)
if cmd.command == AgCmd.HELP:
    return AgCmd.help()

elif cmd.command == AgCmd.GENERAL:
    await update_personal_interest(user, cmd.arguments)
    return await general_query(user, cmd.arguments)

if cmd.command == AgCmd.PERSONAL_INTEREST:
    await update_personal_interest(user, cmd.arguments)
    return f"Updated personal interest to: {get_personal_interest(user)}"

elif cmd.command == AgCmd.WEEKLY:
    if len(cmd.arguments) > 1:
        await update_personal_interest(user, cmd.arguments[1:])
    return f"Articles for your weekly picks:\n\n{"\n\n".join(await get_weekly(user, cmd.arguments))}"

elif cmd.command == AgCmd.WEEKLY_URLS:
    set_weekly_urls(user, cmd.arguments)
    return f"Updated urls for your weekly picks:\n\n {get_weekly_urls(user)}"
```

# Configuration

The bot is configured using a `.env` file:

```bash
# Whichever of the keys is defined is used.
OPENAI_API_KEY=_very_secret_
# ANTHROPIC_API_KEY=_very_secret_

# Connection to the matrix account of the bot
MATRIX_HOME=https://matrix.epfl.ch
MATRIX_LOGIN=username
MATRIX_PASS=password

# Needed to get useful results from the articles
FIRECRAWL_API_KEY=_very_secret_

# If this is set, then all data, session storage, and such, is stored under
# this directory. Defaults to ".".
# DATA_DIR=.

# A comma-separated list of users to allow.
ALLOWED_USERS=@aad:epfl.ch,@cdengler:epfl.ch,@ligasser:epfl.ch
```

# Running

The easiest way to run it is to use [devbox](https://www.jetify.com/docs/devbox/installing_devbox/):

```bash
devbox run bot
```

This takes care of all dependencies, and should run on Mac, Linux, and WSL.

# License

AGPL, what else?

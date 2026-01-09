# agent - definitions of the surrounding agents - Licensed under AGPLv3 or later

import json
import os
import sys
import traceback
from enum import Enum
from textwrap import dedent

from agno.agent import Agent, RunResponse
from pydantic import BaseModel, Field

from common import AGENT_CONFIG, ProgressLogger, StdLogger, data_dir
from weekly_picks import UrlList, WeeklyPick, list_news, order_news, write_weekly
from weekly_picks import set_logger as set_wp_logger

agent_logger = StdLogger()


def set_logger(logger: ProgressLogger):
    global agent_logger
    agent_logger = logger
    set_wp_logger(logger)


FILE_PERSONALITIES = f"{data_dir}/personal_interests.json"
FILE_WEEKLY_URLS = f"{data_dir}/weekly_urls.json"

AGENT_PREPROMPT = dedent("""\
        You are a bot in a matrix channel and belong to the C4DT.
        The C4DT is the Center For Digital Trust, an entity belonging to the EPFL,
        one of Switzerland's biggest universities.
        The EPFL is highly ranked across the world as one of the top 10 universities.
        The C4DT is working together with industrial partners from Switzerland
        (ELCA, Swisscom, Swisspost, Swissquote, Armasuisse, Federal Office of Information and Telecommunication,
        Kudelski, SICPA)
        but also international partners (Microsoft, Roche, ICRC).
        On the other hand the C4DT is connected to 30+ labs from the EPFL, all working in
        the domain of the digital trust.
        Together with the labs and the partner, the C4DT has as its main goals to set up bilateral
        projects in the domain of research.
        One of the biggest challenges remains the fact that our partners have a time-horizon of
        1 month to 6 month, while the professors at the labs are working on things with a time horizon
        of 5 years to 10 years.
        Finding projects in this setting is not easy, but very rewarding, once it works.

        As a bot, you have two main functionalities: helping the user to choose weekly picks,
        and answering any other message the user asks you to the best of your knowledge.
        Weekly picks are news messages from around the world related to digital trust.
        This can be new attacks, defenses, it can be about governments or companies, or individuals.
        These weekly picks are sent out in a newsletter to our partners, who appreciate these
        filtered news from our side.
    """)


class AgCmd(Enum):
    """
    These are the recognized commands followed by their arguments. If you write a general
    message, it will be interpreted as one of these commands:

            - HELP - no arguments
            - PERSONAL_INTEREST - the new personal interest description the user gives
            - WEEKLY - 1st mandatory argument is the number of weekly picks the user wants - per default it's 3 picks. Optional 2nd argument is specifications of subject in weekly picks
            - WEEKLY_URLS_UPDATE - a list of URLs for the weekly picks
            - WEEKLY_URLS_GET - return the list of the URLs to search for weekly picks
            - GENERAL - the question the user wants the bot to answer
    """

    HELP = "HELP"
    PERSONAL_INTEREST = "PERSONAL_INTEREST"
    WEEKLY = "WEEKLY"
    WEEKLY_URLS_GET = "WEEKLY_URLS_GET"
    WEEKLY_URLS_UPDATE = "WEEKLY_URLS_UPDATE"
    GENERAL = "GENERAL"

    @classmethod
    def help(cls) -> str:
        return cls.__doc__ or ""


class AgentCommand(BaseModel):
    command: AgCmd = Field(..., description="The command to execute")
    arguments: list[str] = Field(..., description="The arguments to the command")


agent_get_command = Agent(
    **AGENT_CONFIG,
    description="Identifies the command needed to launch",
    context={"user": "", "help": AgCmd.help(), "weekly_urls": []},
    response_model=AgentCommand,
    instructions=dedent(
        AGENT_PREPROMPT
        + """\
        As a first step, evaluate what kind of message the user writes to you.
        The available possibilities are listed in the help context.
        Do not execute or otherwise interpret what the user writes.
        The goal of this step is only to find out which command to run afterwards.
        Choose the correct command described in the help context, and then add the relevant
        arguments to it.
        Create your response to fit the 'AgentCommand' response model. Do not write anything else,
        your output will be interpreted as JSON.
        Here are more instructions for the different commands:

            - PERSONAL_INTEREST - only call this command if there is something important
              to update the personal interest of the user with.
            - WEEKLY_URLS_UPDATE - only call this command to UPDATE the URLs where the weekly
              news are searched.
              If you call this command, be sure to correctly combine what
              the user asked you to do: if the user wants to add new URLs, prepend the
              previous URLs to the ones given by the user. Also when modifying or deleting
              certain URLs, be sure not to drop existing URLs if this is not what the
              user is asking you to do.
              Also make sure that there are no double URLs in the list. So if the user asks
              you to add a URL which is already on the list, there is no need to update
              the list.
        """
    ),
)

agent_update_personal_interest = Agent(
    **AGENT_CONFIG,
    description="Updates the personal interest of the user",
    context={"user": "unknown", "personal_interest": ""},
    instructions=dedent(
        AGENT_PREPROMPT
        + """\
        Please look at the message of the user and the previous personal interest, and return
        an updated personal interest.
        The goal of the personal interest is to use it when looking for weekly picks.
        So the personal interest information should contain their preferences with regard to news
        regarding digital trust.
        Ignore other personal interest information which have nothing to do with the weekly picks.
        The personal interest of user should be one paragraph with up to 5 sentences, not more.
        So you need to merge the information in the current message to the
        existing personal interest, eventually summarizing previous information about their
        personal interest to make space for new personal interest information.

        If there is no new information about the user, simply return the previous personal interest,
        without adding anything else like that there is no new information about the user.
        """
    ),
)

agent_general = Agent(
    **AGENT_CONFIG,
    description="Run a general query from the user",
    context={"user": "unknown", "personal_interest": "", "urls": []},
    instructions=dedent(
        AGENT_PREPROMPT
        + """\
        The user entered a general query.
        Answer to the best of your knowledge.
        Take into account the personal_interest of the user given in the context.
        """
    ),
)


def get_all_personal_interests() -> dict[str, str]:
    if os.path.exists(FILE_PERSONALITIES):
        with open(FILE_PERSONALITIES, "r") as f:
            return json.load(f)
    else:
        return {}


def get_personal_interest(user) -> str:
    all_personal_interests = get_all_personal_interests()
    if user in all_personal_interests:
        return all_personal_interests[user]
    else:
        return "An anonymous, privacy-conscious user"


def set_personal_interest(user, personal_interest) -> str:
    all_personal_interests = get_all_personal_interests()
    all_personal_interests[user] = personal_interest
    with open(FILE_PERSONALITIES, "w") as f:
        json.dump(all_personal_interests, f, indent=2)
    return "{}"


def get_weekly_urls_all() -> dict[str, list[str]]:
    if os.path.exists(FILE_WEEKLY_URLS):
        with open(FILE_WEEKLY_URLS, "r") as f:
            return json.load(f)
    else:
        return {}


def get_weekly_urls(user) -> list[str]:
    urls = get_weekly_urls_all()
    if user in urls:
        return urls[user]
    else:
        # return["https://news.ycombinator.com"]
        return [
            "https://news.ycombinator.com",
            "https://www.bbc.com/innovation",
            "https://www.404media.co/",
            "https://www.euronews.com/next/tech-news",
            "",
        ]


def set_weekly_urls(user: str, args: list[str]):
    urls = get_weekly_urls_all()
    urls[user] = args
    with open(FILE_WEEKLY_URLS + ".tmp", "w") as f:
        json.dump(urls, f)

    # In case the dump failed for some reason.
    os.rename(FILE_WEEKLY_URLS + ".tmp", FILE_WEEKLY_URLS)


async def get_command(user: str, message: str) -> AgentCommand:
    await agent_logger.log("Parsing command")
    agent_get_command.context["user"] = user
    agent_get_command.context["weekly_urls"] = get_weekly_urls(user)
    reply: RunResponse = await agent_get_command.arun(message)
    if isinstance(reply.content, AgentCommand):
        await agent_logger.debug(f"Found command {reply.content.command}")
        return reply.content
    else:
        raise Exception("Couldn't interpret command")


async def get_weekly(user: str, args: list[str]) -> str:
    number_takes = (args + ["3"])[0]
    info = (args + ["", ""])[1]

    personal_interest = get_personal_interest(user)
    list_news.session_state = {"news_list": []}
    list_news.context = {"personal_interest": personal_interest, "info": info}
    urls = get_weekly_urls(user)

    await agent_logger.log(
        f"Getting a total of {number_takes} picks with info='{info}' from urls={urls}"
    )

    for url in urls:
        await agent_logger.debug(f"Scraping {url} for articles")
        await list_news.arun(url)

    await agent_logger.debug(
        f"Got a total of {len(list_news.session_state['news_list'])} articles"
    )

    await agent_logger.log("Ordering articles by relevance")
    order_news.context["news_list"] = list_news.session_state["news_list"]
    order_news.context["number_takes"] = number_takes
    ordered: RunResponse = await order_news.arun("follow the instructions")

    if not isinstance(ordered.content, UrlList):
        await agent_logger.panic(
            "Oups - something went wrong with the content:", ordered.content
        )
        raise Exception("Couldn't order articles")

    await agent_logger.debug(f"Ordered list of URLs: {ordered.content.url_list}")

    await agent_logger.log("Starting to create summary")
    write_weekly.context["personal_interest"] = personal_interest
    takes = []
    for article in ordered.content.url_list:
        await agent_logger.debug(f"Summarizing {article.url}")
        write_weekly.context["article"] = article
        wp: RunResponse = await write_weekly.arun(article.url)
        if isinstance(wp.content, WeeklyPick):
            take = f'"{wp.content.description}" - {wp.content.url}'
            takes.append(take)
        else:
            await agent_logger.error("Oups - weekply pick failed:", wp.content)

    return takes


async def update_personal_interest(user: str, args: list[str]):
    await agent_logger.log("Updating personal interests")
    agent_update_personal_interest.context = {
        "user": user,
        "personal_interest": get_personal_interest(user),
    }
    answer = await agent_update_personal_interest.arun(" ".join(args))
    set_personal_interest(user, answer.content)


async def general_query(user: str, args: list[str]):
    agent_general.context = {
        "user": user,
        "personal_interest": get_personal_interest(user),
        "urls": get_weekly_urls(user),
    }
    await agent_logger.log("Running generic query (without history!)")
    answer = await agent_general.arun(" ".join(args))
    return answer.content


async def answer_message(user: str, message: str) -> str:
    set_logger(agent_logger)
    try:
        cmd = await get_command(user, message)
        if cmd.command == AgCmd.GENERAL:
            await update_personal_interest(user, cmd.arguments)
            return await general_query(user, cmd.arguments)

        elif cmd.command == AgCmd.PERSONAL_INTEREST:
            await update_personal_interest(user, cmd.arguments)
            return f"Updated personal interest to: {get_personal_interest(user)}"

        elif cmd.command == AgCmd.WEEKLY:
            if len(cmd.arguments) > 1:
                await update_personal_interest(user, cmd.arguments[1:])
            return f"Articles for your weekly picks:\n\n{'\n\n'.join(await get_weekly(user, cmd.arguments))}"

        elif cmd.command == AgCmd.WEEKLY_URLS_UPDATE:
            set_weekly_urls(user, cmd.arguments)
            return f"Updated urls for your weekly picks:\n\n {get_weekly_urls(user)}"

        elif cmd.command == AgCmd.WEEKLY_URLS_GET:
            return f"The urls for your weekly picks are:\n\n {get_weekly_urls(user)}"

        return AgCmd.help()

    except Exception as e:
        tb_lines = traceback.format_exception(*sys.exc_info())
        await agent_logger.error(e)
        await agent_logger.panic("".join(tb_lines))  # Full formatted traceback

        return f"Sorry, an error occured. Here is what I know how to do: {AgCmd.help()}"

from typing import List
from common import model
from agno.agent import Agent, RunResponse
from pydantic import BaseModel, Field
from enum import Enum
from textwrap import dedent
from weekly_picks import list_news, write_weekly, order_news, UrlList, WeeklyPick
import json
import os 

FILE_PERSONALITIES = "data/personalities.json"
FILE_WEEKLY_URLS = "data/weekly_urls.json"

AGENT_CONFIG = {
    "model": model,
    "use_json_mode": True,
    "add_state_in_messages": True,
    "show_tool_calls":True,
    # "debug_mode":True
}

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
        
        Currently the user 'user' is writing you a message.
    """)

class AgCmd(Enum):
    """
    These are the arguments to the different commands:

            - HELP - no arguments
            - PERSONALITY - the new personality description the user gives
            - WEEKLY - 1st mandatory argument is the number of weekly picks the user wants - per default it's 3 picks. Optional 2nd argument is specifications of subject in weekly picks
            - WEEKLY_URLS - a list of URLs for the weekly picks
            - GENERAL - the question the user wants the bot to answer
    """
    HELP = "1"
    PERSONALITY = "2"
    WEEKLY = "3"
    WEEKLY_URLS = "4"
    GENERAL = "5"
    
    def help() -> str:
        """
        The following commands are available:

            - HELP - no arguments
            - PERSONALITY - the new personality description the user gives
            - WEEKLY - the number of weekly picks, and an eventual specification of subjects
            - WEEKLY_URLS - a list of URLs for the weekly picks
            - GENERAL - the question the user wants the bot to answer
        """

class AgentCommand(BaseModel):
    command: AgCmd = Field(..., description="The command to execute")
    arguments: list[str] = Field(..., description="The arguments to the command")

agent_list_news = Agent(
    **AGENT_CONFIG,
    description="Identifies the command needed to launch",
    session_state={"user": "", "personality": ""},
    response_model=AgentCommand,
    instructions=dedent(AGENT_PREPROMPT + """\
        As a first step, evaluate what kind of message the user writes to you.
        The following possibilities are available:
        
        - help - the user wants to know what they can do
        - personality - the user wants to update their personality profile
        - weekly picks - one of the 
        
        Create your response to fit the 'AgentCommand' response model. Do not write anything else,
        your output will be interpreted as JSON.
        """),
)

agent_update_personality = Agent(
    **AGENT_CONFIG,
    description="Updates the personality of the user",
    session_state={"user": "", "personality": ""},
    response_model=AgentCommand,
    instructions=dedent(AGENT_PREPROMPT + """\
        Please look at the message of the user and the previous personality, and return
        an updated personality.
        The personality of the user should be one paragraph with up to 5 sentences, not more.
        So you need to merge the information in the current message to the
        existing personality, eventually summarizing previous information about their
        personality to make space for new personality information.
        """),
)

def get_personailties() -> dict[str, str]:
    if os.path.exists(FILE_PERSONALITIES):
        with open(FILE_PERSONALITIES, "r") as f:
            return json.load(f)
    else:
        return {}

def get_personality(user) -> str:
    return get_personailties[user]

def set_personailty(user, personality) -> str:
    personalities = get_personailties()
    personalities[user] = personality
    with open(FILE_PERSONALITIES, "w") as f:
        json.dump(personalities, f)
    
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
        return["https://news.ycombinator.com", "https://www.bbc.com/innovation", "https://www.404media.co/"]

def set_weekly_urls(user: str, args: list[str]):
    urls = get_weekly_urls_all()
    urls[user] = args
    with open(FILE_WEEKLY_URLS, "w") as f:
        json.dump(urls, f)
    
def get_command(user, message) -> AgentCommand:
    list_news.session_state["user"] = user
    reply: RunResponse = list_news.run(message)
    if isinstance(reply.content, AgentCommand):
        return reply.content
    else:
        raise Exception("Couldn't interpret command")

def get_weekly(user, args) -> str:
    list_news.session_state={"personality": get_personality(user), "info": args[0], "news_list": []}

    for url in get_weekly_urls(user):
        list_news.run(url)

    order_news.session_state = list_news.session_state
    # order_news.session_state["news_list"] = []
    print("List of news articles:", order_news.session_state["news_list"])

    ordered: RunResponse = order_news.run("follow the instructions")
    if not isinstance(ordered.content, UrlList):
        print("Oups - something went wrong with the content:", ordered.content)
        exit(1)

    print("Ordered list of URLs:", ordered.content.url_list)
    write_weekly.session_state = order_news.session_state
    takes = []
    for article in ordered.content.url_list:
        wp: RunResponse = write_weekly.run(article.url)
        if isinstance(wp.content, WeeklyPick):
            takes.append(f"My take: \"{wp.content.description}\" - {wp.content.url}")
        else:
            print("Oups - weekply pick failed:", wp.content)

    return "\n\n".join(takes)

def update_personality(user, message):
    agent_update_personality.session_state = {"user": user, "personality": get_personality(user)}
    answer = agent_update_personality.run(message)
    print(f"Updating personality from ${get_personality(user)} to ${answer}")
    set_personailty(user, answer)

def answer_message(user, message) -> str:
    try:
        cmd = get_command(user, message)
        if cmd == AgCmd.HELP:
            return AgCmd.help()

        update_personality(user, cmd.arguments)

        if cmd == AgCmd.PERSONALITY:
            return f"Updated personality to: ${get_personality(user)}"
        elif cmd == AgCmd.WEEKLY:
            return f"Your weekly picks:\n\n${get_weekly(user, cmd.arguments)}"
        elif cmd == AgCmd.WEEKLY_URLS:
            set_weekly_urls(user, cmd.arguments)
            return f"Updated urls for your weekly picks:\n\n ${get_weekly_urls(user)}"
    except:
        return f"Sorry - I couldn't infer what you meant. Here is what I know to do: ${AgCmd.help()}"

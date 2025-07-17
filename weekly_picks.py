from textwrap import dedent
from agno.agent import Agent, RunResponse
from agno.tools.firecrawl import FirecrawlTools
from pydantic import BaseModel, Field
from markdownify import markdownify as md
from common import ProgressLogger, StdLogger, get_url_cached, model

wp_logger = StdLogger()

def set_logger(logger: ProgressLogger):
    global wp_logger
    wp_logger = logger

# Global configuration for all agents
AGENT_CONFIG = {
    "model": model,
    "use_json_mode": True,
    "add_state_in_messages": True,
    "add_context": True,
    "show_tool_calls": False,
    # "debug_mode": True
}

class NewsSummary(BaseModel):
    url: str = Field(..., description="The URL to the article")
    summary: str = Field(..., description="A short summary of the article")
    dt_relevance: float = Field(..., description="Relevance to digital trust and cybersecurity. 0 = none, 10 = full relevance")
    personal_relevance: float = Field(..., description="Personal relevance with regard to the interest of the querier. 0 = none, 10 = full relevance")

async def get_url(url: str) -> str:
    """This function returns the webpage of the given URL.
    It returns the full description, without any differentiation.

    Args:
        url (str): the URL of the page

    Returns:
        str: the webpage as a markdown"""
    await wp_logger.trace(f"Fetching url {url}")
    return md(get_url_cached(url))

async def add_news(agent: Agent, news: NewsSummary):
    """Adds a new summary to the list of news"""
    await wp_logger.trace(f"Adding news for {news.url}")
    agent.session_state["news_list"].append(news)

list_news = Agent(
    **AGENT_CONFIG,
    description="Fetches the latest news and returns a summary",
    tools=[get_url, add_news],
    session_state={"news_list": []},
    context={"personal_interest": "", "info": ""},
    instructions=dedent("""\
        Visit the url from the prompt, and then choose the 5 most relevant articles related to digital trust to the news_list.
        For the dt_relevance field, only consider the relevance with regard to digital trust, cybersecurity, policy,
        attacks, as well as defenses. Consider articles which talk about defenses or how to fix
        privacy issues higher than articles which only complain about those issues.
        
        You can find the personal_relevance and optional additional infos in the context.
        """),
)

class Url(BaseModel):
    url: str = Field(..., description="The URL to the article")
    
class UrlList(BaseModel):
    url_list: list[Url]

order_news = Agent(
    **AGENT_CONFIG,
    description= "Returns the top articles by relevance",
    context={"number_takes": "3", "news_list": ""},
    instructions=dedent("""\
        You can find a list of articles scraped by the previous agent in the news_list context.
        You need to return the top number_takes articles from this list.
        
        Use the dt_relevance and personal_relevance fields which go from 0 (not relevant) to 10 (very relevant).
        Of course you should also use the summary field.

        For the final reply, only send the JSON, nothing else. Don't introduce the JSON, just send the json.
        The result will be parsed with JSON.parse, so don't introduce it in any way.
        """),
    response_model=UrlList,
)

class WeeklyPick(BaseModel):
    url: str = Field(..., description="The URL to the article")
    description: str = Field(..., description="The paragraph for this weekly pick")

write_weekly = Agent(
    **AGENT_CONFIG,
    description="Write a weekly pick for the article",
    tools=[FirecrawlTools(crawl=False)],
    context={"personal_interest": "", "article": ""},
    instructions= dedent("""\
        For the URL in the prompt, fetch the website, and create a weekly pick.
        A weekly pick has the following format:
        - it is a 1-paragraph, about 500 characters description of the article
        - take into account the personal interest of the requester
        - it puts digital trust in the foreground
        - it should talk about how the problem might be solved
        
        It should highlight why the article has been chosen, but be written from a neutral point of view.
        Write in a nice style, not too formal. Use short sentences, and avoid too complicated words.
        Don't add adverbs and adjectives all over the place.
        
        For the final reply, only send the JSON, nothing else. Don't introduce the JSON, just send the json.
        The result will be parsed with JSON.parse, so don't introduce it in any way.
        
        The personal interest of the user is defined in the personal_interest context.
        You can find previously summarized information about the article in the article context.
        """),
    response_model=WeeklyPick
)


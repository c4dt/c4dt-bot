from textwrap import dedent
from agno.agent import Agent, RunResponse
from agno.tools.firecrawl import FirecrawlTools
from pydantic import BaseModel, Field
from markdownify import markdownify as md
from common import get_url_cached, model

# Change the personality of the weekly-pick writer to match your interests.
personality = dedent("""\
    I am a passionate programmer, software engineer, doing everything from javascript to python, but mainly rust.
    Everything digital trust is very important to me, mostly with regard to how the governments are the best
    protection for the people to protect them against the big corporations with regard to
    privacy, trust, and even security.""")

# Global configuration for all agents
AGENT_CONFIG = {
    "model": model,
    "use_json_mode": True,
    "add_state_in_messages": True,
    "show_tool_calls":True,
    # "debug_mode":True
}

class NewsSummary(BaseModel):
    url: str = Field(..., description="The URL to the article")
    summary: str = Field(..., description="A short summary of the article")
    dt_relevance: float = Field(..., description="Relevance to digital trust and cybersecurity. 0 = none, 10 = full relevance")
    personal_relevance: float = Field(..., description="Personal relevance with regard to the interest of the querier. 0 = none, 10 = full relevance")

def get_url(url: str) -> str:
    """This function returns the webpage of the given URL.
    It returns the full description, without any differentiation.

    Args:
        url (str): the URL of the page

    Returns:
        str: the webpage as a markdown"""
    return md(get_url_cached(url))

def add_news(agent: Agent, news: NewsSummary):
    """Adds a new summary to the list of news"""
    print(f"Adding news {news}")
    agent.session_state["news_list"].append(news)

list_news = Agent(
    **AGENT_CONFIG,
    description="Fetches the latest news and returns a summary",
    tools=[get_url, add_news],
    session_state={"personality": "", "info": "", "news_list": []},
    instructions=dedent("""\
        Visit the url from the prompt, and then choose the 5 most relevant articles related to digital trust to the news_list.
        For the dt_relevance field, only consider the relevance with regard to digital trust, cybersecurity, policy,
        attacks, as well as defenses. Consider articles which talk about defenses or how to fix
        privacy issues higher than articles which only complain about those issues.
        For the personal_relevance, consider the personality of the querier in 'personality'.
        If the 'info' state is not empty, it indicates specific information to look for.
        """),
)

class Url(BaseModel):
    url: str = Field(..., description="The URL to the article")
    
class UrlList(BaseModel):
    url_list: list[Url]

order_news = Agent(
    **AGENT_CONFIG,
    description= "Returns the top 3 articles by relevance",
    session_state={"number_takes": "3"},
    instructions=dedent("""\
        Here is a list of articles scraped by a previous agent:
        
        {news_list}
        
        You need to return the top 'number_takes' articles from this list.
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
    session_state={"personal_interest": ""},
    instructions= dedent("""\
        For the URL in the prompt, fetch the website, and create a weekly pick.
        A weekly pick has the following format:
        - it is a 1-paragraph, about 500 characters personal opinion
        - take into account the 'personal_interest' of the requester
        - it puts digital trust in the foreground
        - it should talk about how the problem might be solved
        
        It should have a personal note and not only be a summary of the article.
        Write in a nice style, not too formal. Use short sentences, and avoid too complicated words.
        Don't add adverbs and adjectives all over the place.
        
        For the final reply, only send the JSON, nothing else. Don't introduce the JSON, just send the json.
        The result will be parsed with JSON.parse, so don't introduce it in any way.
        """),
    response_model=WeeklyPick
)


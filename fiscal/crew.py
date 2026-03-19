import os
from pathlib import Path

import yaml
from crewai import Agent, Crew, Process, Task
from crewai.llm import LLM

from .tools import (
    ArticleContentExtractorTool,
    BelastingdienstStructuredDataTool,
    DutchTaxRateComparatorTool,
    FiscalDeadlineCheckerTool,
    FiscalNewsAggregatorTool,
    GovernmentSiteFetcherTool,
    TaxNewsSearcherTool,
)

CONFIG_DIR = Path(__file__).parent / "config"


def _load_yaml(filename: str) -> dict:
    return yaml.safe_load((CONFIG_DIR / filename).read_text(encoding="utf-8"))


def create_crew(step_callback=None, task_callback=None) -> Crew:
    """Create and return the fiscal monitor crew."""
    agents_config = _load_yaml("agents.yaml")
    tasks_config = _load_yaml("tasks.yaml")

    # Pro model for quality reviewer (needs accuracy)
    reviewer_llm = LLM(
        model="gemini/gemini-3.1-pro-preview",
        api_key=os.environ.get("GEMINI_API_KEY", ""),
    )

    # Flash model for other agents (speed + cost)
    task_llm = LLM(
        model="gemini/gemini-3-flash-preview",
        api_key=os.environ.get("GEMINI_API_KEY", ""),
    )

    # --- Tools ---
    gov_fetcher = GovernmentSiteFetcherTool()
    news_searcher = TaxNewsSearcherTool()
    deadline_checker = FiscalDeadlineCheckerTool(
        config_path=str(CONFIG_DIR / "fiscal_sources.yaml")
    )
    article_extractor = ArticleContentExtractorTool()
    tax_comparator = DutchTaxRateComparatorTool(
        config_path=str(CONFIG_DIR / "tax_rates.yaml")
    )
    news_aggregator = FiscalNewsAggregatorTool()
    bd_data = BelastingdienstStructuredDataTool()

    # --- Agents ---
    fiscal_researcher = Agent(
        **agents_config["fiscal_researcher"],
        tools=[gov_fetcher, news_searcher, deadline_checker, article_extractor, news_aggregator, bd_data],
        llm=task_llm,
        max_iter=50,  # Multiple searches + page fetches
    )

    trend_analyst = Agent(
        **agents_config["trend_analyst"],
        tools=[tax_comparator],
        llm=task_llm,
    )

    blog_writer = Agent(
        **agents_config["blog_writer"],
        tools=[article_extractor, tax_comparator],
        llm=task_llm,
    )

    quality_reviewer = Agent(
        **agents_config["quality_reviewer"],
        tools=[gov_fetcher, article_extractor, bd_data],
        llm=reviewer_llm,
        max_iter=30,  # Source verification fetches
    )

    # --- Tasks ---
    research_task = Task(
        **{k: v for k, v in tasks_config["research_fiscal_topics"].items() if k != "agent"},
        agent=fiscal_researcher,
    )

    analyze_task = Task(
        **{k: v for k, v in tasks_config["analyze_fiscal_trends"].items() if k != "agent"},
        agent=trend_analyst,
        context=[research_task],
    )

    write_task = Task(
        **{k: v for k, v in tasks_config["write_blog_articles"].items() if k != "agent"},
        agent=blog_writer,
        context=[research_task, analyze_task],
    )

    review_task = Task(
        **{k: v for k, v in tasks_config["review_and_finalize"].items() if k != "agent"},
        agent=quality_reviewer,
        context=[write_task],
    )

    # --- Crew ---
    crew_kwargs = dict(
        agents=[fiscal_researcher, trend_analyst, blog_writer, quality_reviewer],
        tasks=[research_task, analyze_task, write_task, review_task],
        process=Process.sequential,
        verbose=True,
    )
    if step_callback:
        crew_kwargs["step_callback"] = step_callback
    if task_callback:
        crew_kwargs["task_callback"] = task_callback

    return Crew(**crew_kwargs)

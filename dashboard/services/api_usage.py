"""Centralized API usage logging with per-provider pricing."""

import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

# Pricing per token (USD)
PRICING = {
    "gemini": {"input": Decimal("0.00000125"), "output": Decimal("0.00001")},
    "anthropic": {"input": Decimal("0.000003"), "output": Decimal("0.000015")},
    "openai": {"input": Decimal("0.000005"), "output": Decimal("0.000015")},
    "google_places": {"per_request": Decimal("0.032")},  # $32 per 1000 requests
    "google_geocoding": {"per_request": Decimal("0.005")},  # $5 per 1000 requests
}


def log_llm_usage(service, input_tokens=0, output_tokens=0, model_name="",
                  job=None, job_pk=None, description=""):
    """Log LLM API usage (Gemini, Anthropic, OpenAI).

    Accepts either a ScanJob instance (job) or a primary key (job_pk).
    """
    try:
        from dashboard.models import APIUsageLog, ScanJob

        input_tokens = input_tokens or 0
        output_tokens = output_tokens or 0
        total_tokens = input_tokens + output_tokens

        pricing = PRICING.get(service, PRICING["gemini"])
        input_cost = Decimal(str(input_tokens)) * pricing["input"]
        output_cost = Decimal(str(output_tokens)) * pricing["output"]
        estimated_cost = (input_cost + output_cost).quantize(Decimal("0.000001"))

        # Resolve job from pk if needed
        if job is None and job_pk:
            try:
                job = ScanJob.objects.get(pk=job_pk)
            except ScanJob.DoesNotExist:
                job = None

        APIUsageLog.objects.create(
            service=service,
            job=job,
            description=description[:300],
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            estimated_cost=estimated_cost,
            api_calls=1,
            model_name=model_name[:100],
        )
    except Exception:
        logger.error("Failed to log LLM usage", exc_info=True)


def log_api_call(service, description="", api_calls=1, job=None, job_pk=None):
    """Log non-LLM API usage (Google Places)."""
    try:
        from dashboard.models import APIUsageLog, ScanJob

        pricing = PRICING.get(service, {})
        per_request = pricing.get("per_request", Decimal("0"))
        estimated_cost = (per_request * api_calls).quantize(Decimal("0.000001"))

        if job is None and job_pk:
            try:
                job = ScanJob.objects.get(pk=job_pk)
            except ScanJob.DoesNotExist:
                job = None

        APIUsageLog.objects.create(
            service=service,
            job=job,
            description=description[:300],
            input_tokens=0,
            output_tokens=0,
            total_tokens=0,
            estimated_cost=estimated_cost,
            api_calls=api_calls,
            model_name="",
        )
    except Exception:
        logger.error("Failed to log API call", exc_info=True)

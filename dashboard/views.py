from django.shortcuts import get_object_or_404, render

from .models import Finding, Report


def home(request):
    status_filter = request.GET.get("status", "")
    reports = Report.objects.all()
    if status_filter:
        reports = reports.filter(status=status_filter)

    if request.htmx:
        return render(request, "dashboard/_report_list.html", {"reports": reports, "status_filter": status_filter})

    return render(request, "dashboard/home.html", {"reports": reports, "status_filter": status_filter})


def report_detail(request, pk):
    report = get_object_or_404(Report, pk=pk)
    return render(request, "dashboard/report_detail.html", {"report": report})


def htmx_report_list(request):
    status_filter = request.GET.get("status", "")
    reports = Report.objects.all()
    if status_filter:
        reports = reports.filter(status=status_filter)
    return render(request, "dashboard/_report_list.html", {"reports": reports, "status_filter": status_filter})


def htmx_report_card(request, pk):
    report = get_object_or_404(Report, pk=pk)
    return render(request, "dashboard/_report_card.html", {"report": report})


def htmx_finding_detail(request, pk):
    finding = get_object_or_404(Finding, pk=pk)
    return render(request, "dashboard/_finding_detail.html", {"finding": finding})

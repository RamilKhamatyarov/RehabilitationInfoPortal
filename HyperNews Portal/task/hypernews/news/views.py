import datetime
import json
from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from django.conf import settings
from django import forms


class MainPageView(View):

    def get(self, request, *args, **kwargs):
        return redirect("/news/")


class NewsListView(View):

    def get(self, request, *args, **kwargs):
        data = []
        with open(settings.NEWS_JSON_PATH, 'r') as f:
            data = json.load(f)
            q = request.GET.get('q')
            for d in data:
                dd = d
                if q and q in d['title']:
                    ded = self.findnewsbylink(data, dd['link'])
                    ded['created'] = datetime.strptime(ded['created'], "%Y-%m-%d %H:%M:%S").date().strftime("%Y-%m-%d")
                    return render(request, 'index.html', {"searched": ded})

        with open(settings.NEWS_JSON_PATH, 'r') as f:
            data = json.load(f)

        data.sort(key=lambda date: datetime.strptime(date['created'], "%Y-%m-%d %H:%M:%S"), reverse=True)

        for d in data:
            d['created'] = datetime.strptime(d['created'], "%Y-%m-%d %H:%M:%S").date().strftime("%Y-%m-%d")

        return render(request, 'index.html', {"list": data})

    @staticmethod
    def findnewsbylink(array, id):
        for data in array:
            if data['link'] == id:
                return data


class NewsView(View):
    def get(self, request, id):
        data = []
        with open(settings.NEWS_JSON_PATH, 'r') as f:
            data = json.load(f)

        data = self.findnewsbylink(data, id)
        return render(request, 'index.html', {"content": data})

    @staticmethod
    def findnewsbylink(array, id):
        for data in array:
            if data['link'] == id:
                return data


class CreateNewsForm(forms.Form):
    title = forms.CharField(required=False)
    text = forms.CharField(required=False)


class CreateNewsView(View):
    @csrf_exempt
    def get(self, request):
        form = CreateNewsForm()
        return render(request, 'index.html', {"source": form})

    @csrf_exempt
    def post(self, request):
        data = []
        with open(settings.NEWS_JSON_PATH, 'r') as f:
            data = json.load(f)

            form = CreateNewsForm(request.POST)

            if request.method == "POST" and form.is_valid():
                data.append(
                    {
                        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "title": form.cleaned_data['title'],
                        "text": form.cleaned_data['text'],
                        "link": data[-1]['link'] + 1
                    }
                )

        with open(settings.NEWS_JSON_PATH, "w") as f:
            json.dump(data, f)

        return redirect("/news/")

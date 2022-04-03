from logging import PlaceHolder
from pickle import NONE, TRUE
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from . import util
from markdown2 import Markdown
import secrets

class NewEntryForm(forms.Form):
    # To use to create and edit entries
    title = forms.CharField(widget=forms.TextInput(attrs={'placeholder' : 'Title'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'myfieldclass', 'placeholder' : 'Text Area'}))
    edit= forms.BooleanField(initial=False, widget=forms.HiddenInput(), required=False)

def index(request):
    # Render index with the list of entries
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, entry):
    # Convert md in HTML
    markdowner = Markdown()
    contentpage = util.get_entry(entry)
    return render(request, "encyclopedia/wiki.html", {
        "wikis": markdowner.convert(contentpage),
        "entryTitle": entry
    })

def search(request):
    # take the results of form
    value= request.GET.get('q', '')
    if(util.get_entry(value) is not None):
        return HttpResponseRedirect(reverse('entry', kwargs={'entry': value}))
    else:
        subStringEntries = []
        for entry in util.list_entries():
            if value.upper() in entry.upper():
                subStringEntries.append(entry)

        return render(request, "encyclopedia/index.html", {
            "entries": subStringEntries,
            "search": True,
            "value": value
        })


def create(request):
    # if the data is sent
    if request.method == "POST":
        form = NewEntryForm(request.POST)
        # check if form is valid and clean
        if form.is_valid():
            # take the information
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            # check if we already have the same entry or if we are editting it
            if(util.get_entry(title) is None or form.cleaned_data["edit"] is True):
                # Save the content
                util.save_entry(title,content)
                # Use the entry function with the title as entry
                return HttpResponseRedirect(reverse("entry", kwargs={'entry': title}))
            else:
                # we return the form, the entry and say that the page already exist
                return render(request, "encyclopedia/create.html", {
                    "form": form,
                    "exist": True,
                    "entry": title
                })
        else:
            return render(request, "encyclopedia/create.html", {
            "form":form,
            "exist": False
            })
    # When the method is get 
    else:
        return render(request, "encyclopedia/create.html", {
        "form": NewEntryForm(),
        "exist": False
        })


def edit(request, entry):
    page = util.get_entry(entry)
    if page is None:
        # if not exist will give one error message
        return render(request, "encyclopedia/noEntry.html", {
            "EntryTitle": entry
        })
    else:
        # Create a new form (edit)
        form= NewEntryForm()
        form.fields["title"].initial = entry
        form.fields["title"].widget = forms.HiddenInput()
        form.fields["content"].initial = page
        # The same of a create page but now we are saying that we are editting that!
        form.fields["edit"].initial = True
        return render(request, "encyclopedia/create.html", {
            "form": form,
            "edit": form.fields["edit"].initial,
            "etitle": form.fields["title"].initial
        })

def randomize(request):
    # bring all entries
    wiki= util.list_entries()
    # random to one
    random = secrets.choice(wiki)
    return HttpResponseRedirect(reverse("entry", kwargs={"entry":random}))
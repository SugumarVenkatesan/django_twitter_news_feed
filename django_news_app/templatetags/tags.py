from django import template
from collections import namedtuple
from operator import itemgetter
from django_news_app.forms import NewsListForm
register = template.Library()


@register.filter
def gt(form,field):
    Choices  = namedtuple('Choice', 'name value')
    if isinstance(form,NewsListForm):
        form = NewsListForm()
        form = form.fields.get(field.name)
        return form 
    if isinstance(field,list):
        if len(field) > 0:
           form.choices = [Choices(name=each,value=each) for each in map(itemgetter(0),field)]
        return form.choices 
    return None
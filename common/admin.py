from django.contrib import admin
from common.model.votes import BlogVotes
from common.model.other import PhoneCodes


class BlogVotesAdmin(admin.ModelAdmin):
    list_display = (
        'vote',
        'user',
        #'parent',
    )

admin.site.register(BlogVotes, BlogVotesAdmin)
admin.site.register(PhoneCodes)

from django.contrib import admin
from .models import *

# Register your models here.

class MediaFileAdmin(admin.ModelAdmin):
    list_display = ('title', 'module',) 
    exclude = ('thumbnail',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields.pop('thumbnail', None)
        print('request - ', request.GET, request.POST, request.file, request.body)
        return form
    

admin.site.register(User)
admin.site.register(Question)
admin.site.register(Test)
admin.site.register(QuestionTest)
admin.site.register(MediaFile, MediaFileAdmin)
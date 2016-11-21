from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _

# Register your models here.
from .models import Redditer, Moderator
from .forms import RedditerChangeForm, RedditerCreationForm

class RedditerAdmin(UserAdmin):
    # The forms to add and change user instances

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference the removed 'username' field
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2')}
        ),
    )
    form = RedditerChangeForm
    add_form = RedditerCreationForm
    list_display = ('joined_on', 'username', 'email')
    search_fields = ('email', 'username')

class ModeratorAdmin(admin.ModelAdmin):
	list_display = ('redditer', 'subreddit')

admin.site.register(Redditer, RedditerAdmin)
admin.site.register(Moderator, ModeratorAdmin)

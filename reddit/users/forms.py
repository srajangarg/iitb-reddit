from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import RedditUser

class RedditUserCreationForm(UserCreationForm):
    """
    A form that creates a user, with no privileges, from the given email and
    password.
    """

    def __init__(self, *args, **kargs):
        super(RedditUserCreationForm, self).__init__(*args, **kargs)
        # del self.fields['username']

    class Meta:
        model = RedditUser
        fields = ("email",)

class RedditUserChangeForm(UserChangeForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """

    def __init__(self, *args, **kargs):
        super(RedditUserChangeForm, self).__init__(*args, **kargs)
        # del self.fields['username']

    class Meta:
        model = RedditUser
        fields = ("email",)
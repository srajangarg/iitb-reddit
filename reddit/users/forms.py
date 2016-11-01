from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import Redditer

class RedditerCreationForm(UserCreationForm):
    """
    A form that creates a user, with no privileges, from the given email and
    password.
    """

    def __init__(self, *args, **kargs):
        super(RedditerCreationForm, self).__init__(*args, **kargs)
        # del self.fields['username']

    class Meta:
        model = Redditer
        fields = ("email",)

class RedditerChangeForm(UserChangeForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """

    def __init__(self, *args, **kargs):
        super(RedditerChangeForm, self).__init__(*args, **kargs)
        # del self.fields['username']

    class Meta:
        model = Redditer
        fields = ("email",)
"""Admin Views"""
from flask_admin.contrib.sqla import ModelView
from wtforms import PasswordField


class UserAdmin(ModelView):
    """View model User"""
    form_columns = ['first_name', 'last_name', 'password', 'email',
                    "birth_date", "gender", "profile_picture",
                    "description", "status"]
    form_extra_fields = {
        'password': PasswordField('Password')
    }

    def on_model_change(self, form, model, is_created):
        if form.password.data:
            model.password = form.password.data

from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.forms import UserCreationForm

from apps.models import Students, Users


admin.site.register(Students)


@admin.register(Users)
class UserAdmin(ModelAdmin):
    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_active",
    )
    add_form = UserCreationForm

    # Ensure that when creating or updating users, passwords are hashed
    def save_model(self, request, obj, form, change):
        if form.cleaned_data["password"]:
            obj.set_password(form.cleaned_data["password"])
        super().save_model(request, obj, form, change)

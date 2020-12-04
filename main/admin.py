from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from main.forms import CustomUserCreationForm, CustomUserChangeForm 
from main.models import CustomUser
from main.models import Profile
from blog.models import Note, Tag


admin.site.site_header = "Post Admin Site"

class CustomUserProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'User Profile'
    fk_name = 'user'


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin): 
    inlines = (CustomUserProfileInline,)
    add_form = CustomUserCreationForm 
    form = CustomUserChangeForm 
    model = CustomUser

    list_display = ['email', 'username', 'birthdate', 'is_staff', ]
    fieldsets = UserAdmin.fieldsets + ( 
        (None, {'fields': ('birthdate',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + ( 
        (None, {'fields': ('birthdate',)}),
    )
    # def get_inline_instances(self, request, obj=None):
    #     if not obj:
    #         return list()
    #     return super(CustomUserAdmin, self).get_inline_instances(request, obj)





# class ProfileAdmin(UserAdmin):
#     inlines = (ProfileInline, )
#     list_display = ('username', 'email', 'first_name',
#                     'last_name', 'is_staff', )
#     list_select_related = ('profile', )

#     def get_inline_instances(self, request, obj=None):
#         if not obj:
#             return list()
#         return super(ProfileAdmin, self).get_inline_instances(request, obj)

#     from typing import Set

#     def get_form(self, request, obj=None, **kwargs):
#         form = super().get_form(request, obj, **kwargs)
#         is_superuser = request.user.is_superuser
#         disabled_fields = set()  # type: Set[str]

#         if not is_superuser:
#             disabled_fields |= {
#                 'username',
#                 'is_superuser',
#                 'user_permissions',
#             }

#         # Prevent non-superusers from editing their own permissions
#         if (
#             not is_superuser
#             and obj is not None
#             and obj == request.user
#         ):
#             disabled_fields |= {
#                 'is_staff',
#                 'is_superuser',
#                 'groups',
#                 'user_permissions',
#             }

#         for f in disabled_fields:
#             if f in form.base_fields:
#                 form.base_fields[f].disabled = True

#         return form


# admin.site.unregister(User)
# admin.site.register(User, ProfileAdmin)




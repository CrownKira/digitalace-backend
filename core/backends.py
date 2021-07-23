# TODO: use backend for authorization?


# from django.contrib.auth.backends import ModelBackend


# class RolePermissionBackend(ModelBackend):
#     def get_role_permissions(user_obj, obj=None):
#         return user_obj.get_role_permissions()

#     def get_all_permissions(self, user_obj, obj=None):
#         return {
#             *self.get_user_permissions(user_obj, obj=obj),
#             *self.get_group_permissions(user_obj, obj=obj),
#             *self.get_role_permissions(user_obj, obj=obj),
#         }

#     def has_perm(self, user_obj, perm, obj=None):
#         return user_obj.is_active and perm in self.get_all_permissions(
#             user_obj, obj=obj
#         )

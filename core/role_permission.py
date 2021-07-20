from rest_framework.permissions import DjangoModelPermissions


class RolePermission(DjangoModelPermissions):
    """Role permission"""

    def has_permission(self, request, view):
        # Workaround to ensure DjangoModelPermissions are not applied
        # to the root view when using DefaultRouter.
        if getattr(view, "_ignore_model_permissions", False):
            return True

        if not request.user or (
            not request.user.is_authenticated and self.authenticated_users_only
        ):
            return False

        queryset = self._queryset(view)
        print("kw3")
        print(request.method)
        print("kw3")
        print(queryset.model)
        perms = self.get_required_permissions(request.method, queryset.model)

        print("kw2")
        print(perms)
        return request.user.has_role_perms(perms)

    # def has_permission(self, request, view):
    #     # Workaround to ensure DjangoModelPermissions are not applied
    #     # to the root view when using DefaultRouter.
    #     if getattr(view, "_ignore_model_permissions", False):
    #         return True

    #     if not request.user or (
    #         not request.user.is_authenticated and self.authenticated_users_only
    #     ):
    #         return False

    #     queryset = self._queryset(view)
    #     perms = self.get_required_permissions(request.method, queryset.model)
    #     print("kww")
    #     print(perms)

    #     return request.user.has_perms(perms)

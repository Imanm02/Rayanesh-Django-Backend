from import_export import resources, fields

from .models import Profile


class ProfileResource(resources.ModelResource):
    username = fields.Field(attribute='user__username', column_name='username')
    email = fields.Field(attribute='user__email', column_name='email')
    class Meta:
        model = Profile
        fields = ('username', 'name', 'email', 'university_degree', 'image')
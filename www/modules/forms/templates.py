from www               import config
from www.modules.forms import SelectField


class PermissionsSelect(SelectField):
    ''' Select field listing permissions. Use all=True to list all permissions. Otherwise will only show up to the users permission level '''
    def __init__(self, all=False, *args, **kwargs ) -> None:
        kwargs['_id'] = kwargs.get('_id', 'permissions')
        self.all = all
        kwargs['option_list'] = self.__buildOptionsList()
        super().__init__(*args, **kwargs)
        
    def __buildOptionsList(self):
        permission_list = config.Permissions.__dict__
        option_list = []
        for permission, value in permission_list.items():
            if permission[0] != '_':
                option_list.append({
                    'txt': permission.replace('_', ' ').capitalize(),
                    'value': value,
                    'selected': True if value == 1 else False
                })
        return option_list



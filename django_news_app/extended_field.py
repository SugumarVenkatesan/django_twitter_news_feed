from django.db import models

class ListField(models.TextField):

    __metaclass__ = models.SubfieldBase
    
    def __init__(self, save_list=list(),*args, **kwargs ):
        self.save_list = save_list
        super(ListField, self).__init__(self.save_list, *args, **kwargs)
            
    def to_python(self, value):
        if value == "":
            return None
        try:
            if isinstance(value, list):
                del self.save_list[:]
                self.save_list.extend(value)
            return self.save_list
        except ValueError:
            pass
        return value

    def get_db_prep_save(self, value, *args, **kwargs):
        if not value:
            return None
        if isinstance(value, list):
            value = ','.join(each for each in value)
        return super(ListField, self).get_db_prep_save(value, *args, **kwargs)

from copy import deepcopy


class PopulateModel:
    def __init__(self, model, update_in_case_of_change=True, fields_to_ignore=None):
        self.model_class = model
        self.update_in_case_of_change = update_in_case_of_change
        self.fixed_fields_to_ignore = ('_state', 'id', 'created_on', 'updated_at')
        self.overall_fields_to_ignore = self._add_fields_to_ignore(fields_to_ignore)

    def create_or_update(self, model):
        if self.update_in_case_of_change:
            self._update_if_exists_or_create(model)
        else:
            model.save()

    def _get_model_dict(self, model):
        model_dict = deepcopy(model.__dict__)
        self._remove_fields_to_ignore(model_dict)
        return model_dict

    def _add_fields_to_ignore(self, additional_fields_to_ignore):
        fields_to_ignore = list(self.fixed_fields_to_ignore)
        if additional_fields_to_ignore:
            fields_to_ignore += additional_fields_to_ignore
        return fields_to_ignore

    def _remove_fields_to_ignore(self, model_dict):
        for key in self.overall_fields_to_ignore:
            model_dict.pop(key, None)

    def _update_or_create_model(self, model, model_dict):
        existing_model = list(self.model_class.objects.filter(**model_dict))
        if existing_model:
            self._update_existing_model(existing_model[0], model)
        else:
            model.save()

    def _update_existing_model(self, existing_model, model):
        model.id = existing_model.id
        model.created_on = existing_model.created_on
        model.save()

    def _update_if_exists_or_create(self, model):
        model_dict = self._get_model_dict(model)
        self._update_or_create_model(model, model_dict)

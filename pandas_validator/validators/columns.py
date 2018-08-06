from pandas_validator.validators.series import (
    BaseSeriesValidator,
    IntegerSeriesValidator,
    FloatSeriesValidator,
    CharSeriesValidator,
    LambdaSeriesValidator,
    EncodingSeriesValidator
)

from pandas_validator.core.exceptions import ValidationError
from pandas_validator.core.constants import ERROR_TYPES


class ColumnValidatorMixin(BaseSeriesValidator):
    def __init__(self, label, required=True, *args, **kwargs):
        super(ColumnValidatorMixin, self).__init__(*args, **kwargs)
        self.label = label
        self.required = required

    def validate(self, dataframe):
        try:
            super(ColumnValidatorMixin, self).validate(dataframe[self.label])
        except KeyError:
            if self.required:
                error_type = ERROR_TYPES['required_field_error']
                raise ValidationError('Series has the value greater than max.', error_type, self.label)


class IntegerColumnValidator(ColumnValidatorMixin, IntegerSeriesValidator):
    pass


class FloatColumnValidator(ColumnValidatorMixin, FloatSeriesValidator):
    pass


class CharColumnValidator(ColumnValidatorMixin, CharSeriesValidator):
    pass


class EncodingColumnValidator(ColumnValidatorMixin, EncodingSeriesValidator):
    pass


class LambdaColumnValidator(ColumnValidatorMixin, LambdaSeriesValidator):
    pass

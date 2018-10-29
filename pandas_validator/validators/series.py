import numpy as np

from pandas_validator.core.exceptions import BasicValidationError, ValidationError
from pandas_validator.core.constants import ERROR_TYPES


def convert_list_to_simple_int(numpy_list):
    return [int(x) for x in numpy_list]
    
    
class BaseSeriesValidator(object):
    def __init__(self, series_type=None):
        self.series_type = series_type

    def validate(self, series):
        self._check_type(series)

    def _check_type(self, series):
        if self.series_type is not None:
            if not np.issubdtype(series.dtype.type, self.series_type):
                error_type = ERROR_TYPES['different_types']
                raise ValidationError('Series has the different type variables.', error_type, series.name)

    def is_valid(self, series):
        try:
            self.validate(series)
        except (BasicValidationError, ValidationError):
            return False
        else:
            return True


class IntegerSeriesValidator(BaseSeriesValidator):
    def __init__(self, min_value=None, max_value=None, series_type=np.int64):
        super(IntegerSeriesValidator, self).__init__(series_type)

        self.max_value, self.min_value = max_value, min_value

    def validate(self, series):
        super(IntegerSeriesValidator, self).validate(series)

        self.check_max_values(series)
        self.check_min_values(series)

    def check_max_values(self, series):
        if self.max_value is not None:
            check_list = series[series > self.max_value]
            if len(check_list) > 0:
                numpy_idx = check_list.index.tolist()
                idx = convert_list_to_simple_int(numpy_idx)
                error_type = ERROR_TYPES['out_of_range']
                raise ValidationError('Series has the value greater than max.', error_type, series.name, idx)

    def check_min_values(self, series):
        if self.min_value is not None:
            check_list = series[series < self.min_value]
            if len(check_list) > 0:
                numpy_idx = check_list.index.tolist()
                idx = convert_list_to_simple_int(numpy_idx)
                error_type = ERROR_TYPES['out_of_range']
                raise ValidationError('Series has the value smaller than min.', error_type, series.name, idx)


class FloatSeriesValidator(IntegerSeriesValidator):
    def __init__(self, series_type=np.float64, *args, **kwargs):
        super(FloatSeriesValidator, self).__init__(series_type=series_type,
                                                   *args, **kwargs)

    def validate(self, series):
        super(FloatSeriesValidator, self).validate(series)

        self.check_nan_field(series)

    def check_nan_field(self, series):
        if series.isnull().any():
            numpy_idx = series[series.isnull()].index.tolist()
            idx = convert_list_to_simple_int(numpy_idx)
            error_type = ERROR_TYPES['empty_field']
            raise ValidationError('Float series has the empty field.', error_type, series.name, idx)


class NumberSeriesValidator(FloatSeriesValidator):
    def __init__(self, series_type=np.number, *args, **kwargs):
        super(NumberSeriesValidator, self).__init__(series_type=series_type,
                                                    *args, **kwargs)


class CharSeriesValidator(BaseSeriesValidator):
    def __init__(self, min_length=None, max_length=None, *args, **kwargs):
        super(CharSeriesValidator, self).__init__(*args, **kwargs)

        self.min_length, self.max_length = min_length, max_length

    def _check_type(self, series):
        if len(series[series.map(lambda x: not isinstance(x, str))]) > 0:
            error_type = ERROR_TYPES['different_types']
            raise ValidationError('Series has the different type variables.', error_type, series.name)

    def validate(self, series):
        super(CharSeriesValidator, self).validate(series)

        self.check_max_length(series)
        self.check_min_length(series)

    def check_max_length(self, series):
        if self.max_length is not None:
            series_str_sizes = series.str.len()
            oversized = series_str_sizes[series_str_sizes > self.max_length]
            if len(oversized) > 0:
                numpy_idx = oversized.index.tolist()
                idx = convert_list_to_simple_int(numpy_idx)
                error_type = ERROR_TYPES['string_size']
                raise ValidationError('Series has the length greater than max.', error_type, series.name, idx)

    def check_min_length(self, series):
        if self.min_length is not None:
            series_str_sizes = series.str.len()
            smallsized = series_str_sizes[series_str_sizes < self.min_length]
            if len(smallsized) > 0:
                numpy_idx = smallsized.index.tolist()
                idx = convert_list_to_simple_int(numpy_idx)
                error_type = ERROR_TYPES['string_size']
                raise ValidationError('Series has the length smaller than min.', error_type, series.name, idx)


class EncodingSeriesValidator(BaseSeriesValidator):
    def __init__(self, *args, **kwargs):
        super(EncodingSeriesValidator, self).__init__(*args, **kwargs)

    def validate(self, series):
        super(EncodingSeriesValidator, self).validate(series)

        not_english = ~series.apply(self.check_encoding)
        if not_english.any():
            numpy_idx = series[not_english].index.tolist()
            idx = convert_list_to_simple_int(numpy_idx)
            error_type = ERROR_TYPES['encoding_error']
            raise ValidationError('Series has non English characters', error_type, series.name, idx)

    @staticmethod
    def check_encoding(string):
        try:
            string.encode('utf-8').decode('ascii')
            string.encode('ascii')
        except (UnicodeEncodeError, UnicodeDecodeError):
            return False
        else:
            return True


class LambdaSeriesValidator(BaseSeriesValidator):
    def __init__(self, function, *args, **kwargs):
        super(LambdaSeriesValidator, self).__init__(*args, **kwargs)

        self.function = function

    def _check_type(self, series):
        pass

    def validate(self, series):
        super(LambdaSeriesValidator, self).validate(series)

        if (not self.function(series)):
            raise BasicValidationError('Validator function returned False.')

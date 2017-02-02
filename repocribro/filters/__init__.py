from .common import common_filters
from .models import model_filters

all_filters = {
    **common_filters,
    **model_filters
}

__all__ = ['all_filters', 'register_filters_from_dict']

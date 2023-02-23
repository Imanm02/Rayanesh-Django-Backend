import django_filters

from issue.models import Issue
from podcast.models import Podcast
from blog.models import BlogPost

CHOICES = (
    ('ascending', 'Ascending'),
    ('descending', 'Descending')
)


class IssueFilter(django_filters.FilterSet):
    publishing_date__gte = django_filters.DateFilter(field_name='publishing_date',
                                                     lookup_expr='gte',
                                                     label='Publishing Date Start')
    publishing_date__lte = django_filters.DateFilter(field_name='publishing_date',
                                                     lookup_expr='lte',
                                                     label='Publishing Date End')
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains', label='Name')
    subject = django_filters.ChoiceFilter(field_name='subject', lookup_expr='icontains', label='Subject')
    publishing_date__year = django_filters.NumberFilter(field_name='publishing_date',
                                                        lookup_expr='year', label='Publishing Year')
    ordering = django_filters.ChoiceFilter(label='Order by Views', choices=CHOICES, method='filter_by_order')

    class Meta:
        model = Issue
        exclude = ('id', 'created', 'modified', 'raw_file', 'cover_image',
                   'authors', 'pages_number', 'is_issue',)

    def filter_by_order(self, queryset, name, value):
        expression = 'views_count' if value.lower() == 'ascending' else '-views_count'
        return queryset.order_by(expression)


class PodcastFilter(django_filters.FilterSet):
    publishing_date__gte = django_filters.DateFilter(field_name='publishing_date',
                                                     lookup_expr='gte',
                                                     label='Publishing Date Start')
    publishing_date__lte = django_filters.DateFilter(field_name='publishing_date',
                                                     lookup_expr='lte',
                                                     label='Publishing Date End')
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains', label='Name')
    subject = django_filters.CharFilter(field_name='subject', lookup_expr='icontains', label='Subject')
    publishing_date__year = django_filters.NumberFilter(field_name='publishing_date',
                                                        lookup_expr='year', label='Publishing Year')
    ordering = django_filters.ChoiceFilter(label='Order by Views', choices=CHOICES, method='filter_by_order')

    def filter_by_order(self, queryset, name, value):
        expression = 'views_count' if value.lower() == 'ascending' else '-views_count'
        return queryset.order_by(expression)

    class Meta:
        model = Podcast
        exclude = ('id', 'created', 'modified', 'raw_file', 'cover_image',
                   'contributors', 'length')


class BlogFilter(django_filters.FilterSet):
    posting_date__gte = django_filters.DateFilter(field_name='posting_date',
                                                  lookup_expr='gte',
                                                  label='Posting Date Start')
    posting_date__lte = django_filters.DateFilter(field_name='posting_date',
                                                  lookup_expr='lte',
                                                  label='Posting Date End')
    posting_date__year = django_filters.NumberFilter(field_name='posting_date',
                                                     lookup_expr='year', label='Posting Year')
    subject = django_filters.CharFilter(field_name='subject', lookup_expr='icontains', label='Subject')
    ordering = django_filters.ChoiceFilter(label='Order by Views', choices=CHOICES, method='filter_by_order')

    class Meta:
        model = BlogPost
        exclude = ('id', 'created', 'modified', 'post_text', 'post_image', 'contributors',
                   'reading_time',)

    def filter_by_order(self, queryset, name, value):
        expression = 'views_count' if value.lower() == 'ascending' else '-views_count'
        return queryset.order_by(expression)

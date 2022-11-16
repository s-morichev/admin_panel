from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q, Value
from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView
from movies.models import Filmwork, PersonFilmwork

PersonRoles = PersonFilmwork.PersonRoles


class MoviesApiMixin:
    model = Filmwork
    http_method_names = ["get"]

    def get_queryset(self):
        qs = (
            self.model.objects.prefetch_related("genres", "persons")
            .values("id", "title", "description", "creation_date", "rating", "type")
            .annotate(genres=ArrayAgg("genres__name", distinct=True, default=Value([])))
            .annotate(
                actors=ArrayAgg(
                    "persons__full_name",
                    filter=Q(personfilmwork__role=PersonRoles.ACTOR),
                    distinct=True,
                    default=Value([]),
                ),
            )
            .annotate(
                directors=ArrayAgg(
                    "persons__full_name",
                    filter=Q(personfilmwork__role=PersonRoles.DIRECTOR),
                    distinct=True,
                    default=Value([]),
                ),
            )
            .annotate(
                writers=ArrayAgg(
                    "persons__full_name",
                    filter=Q(personfilmwork__role=PersonRoles.WRITER),
                    distinct=True,
                    default=Value([]),
                ),
            )
        )

        return qs

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):
    paginate_by = 50

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = self.get_queryset()
        paginator, page, queryset, is_paginated = self.paginate_queryset(
            queryset,
            self.paginate_by,
        )
        context = {
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "prev": page.previous_page_number() if page.has_previous() else None,
            "next": page.next_page_number() if page.has_next() else None,
            "results": list(page.object_list),
        }
        return context


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):
    def get_context_data(self, **kwargs):
        return kwargs["object"]

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Filmwork, Genre, Person


class GenreFilmworkInline(admin.TabularInline):
    model = Filmwork.genres.through
    extra = 0


class PersonForFilmworkInline(admin.TabularInline):
    model = Filmwork.persons.through
    extra = 0
    autocomplete_fields = ("person",)


class FilmworkForPersonInline(admin.TabularInline):
    model = Filmwork.persons.through
    extra = 0
    autocomplete_fields = ("film_work",)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("full_name", "get_film_works")
    search_fields = ("full_name",)
    inlines = (FilmworkForPersonInline,)

    def get_film_works(self, obj):
        return ", ".join(film_work.title for film_work in obj.film_works.all())

    get_film_works.short_description = _("film_works of person")

    def get_queryset(self, request):
        queryset = super().get_queryset(request).prefetch_related("film_works")
        return queryset


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "type",
        "creation_date",
        "rating",
        "get_genres",
        "get_persons",
    )
    list_filter = ("type",)
    search_fields = ("title",)
    inlines = (GenreFilmworkInline, PersonForFilmworkInline)

    def get_genres(self, obj):
        return ", ".join(genre.name for genre in obj.genres.all())

    def get_persons(self, obj):
        return ", ".join(person.full_name for person in obj.persons.distinct())

    get_genres.short_description = _("genres of film_work")
    get_persons.short_description = _("persons of film_work")

    def get_queryset(self, request):
        queryset = super().get_queryset(request).prefetch_related("genres", "persons")
        return queryset

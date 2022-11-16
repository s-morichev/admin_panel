import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(_("name"), max_length=255)
    description = models.TextField(_("description"), blank=True)

    class Meta:
        db_table = "genre"
        ordering = ("name",)
        verbose_name = _("genre")
        verbose_name_plural = _("genres")
        indexes = (models.Index(fields=("name",), name="genre_name"),)

    def __str__(self):
        return self.name


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.CharField(_("full_name"), max_length=255)

    class Meta:
        db_table = "person"
        ordering = ("full_name",)
        verbose_name = _("person")
        verbose_name_plural = _("persons")
        indexes = (models.Index(fields=("full_name",), name="person_full_name"),)

    def __str__(self):
        return self.full_name


class Filmwork(UUIDMixin, TimeStampedMixin):
    class FilmworkTypes(models.TextChoices):
        MOVIE = "movie", _("movie type")
        TV_SHOW = "tv_show", _("tv-show type")

    title = models.CharField(_("title"), max_length=255)
    description = models.TextField(_("description"), blank=True)
    creation_date = models.DateField(_("creation_date"), blank=True, null=True)
    rating = models.FloatField(
        _("rating"),
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
    )
    type = models.CharField(_("type"), max_length=255, choices=FilmworkTypes.choices)
    genres = models.ManyToManyField(
        Genre,
        through="GenreFilmwork",
        verbose_name=_("genres"),
        related_name="film_works",
    )
    persons = models.ManyToManyField(
        Person,
        through="PersonFilmwork",
        verbose_name=_("persons"),
        related_name="film_works",
    )

    class Meta:
        db_table = "film_work"
        ordering = ("title",)
        verbose_name = _("film_work")
        verbose_name_plural = _("film_works")
        indexes = (
            models.Index(fields=("title",), name="film_work_title"),
            models.Index(fields=("creation_date",), name="film_work_creation_date"),
            models.Index(fields=("rating",), name="film_work_rating"),
        )

    def __str__(self):
        return self.title


class GenreFilmwork(UUIDMixin):
    film_work = models.ForeignKey(
        Filmwork,
        on_delete=models.CASCADE,
        db_index=False,
        verbose_name=_("film_work for genre"),
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        db_index=False,
        verbose_name=_("genre for film_work"),
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "genre_film_work"
        verbose_name = _("genre of filmwork")
        verbose_name_plural = _("genres of filmwork")
        constraints = (
            models.UniqueConstraint(
                fields=("genre", "film_work"),
                name="film_work_genre",
            ),
        )

    def __str__(self):
        return ""


class PersonFilmwork(UUIDMixin):
    class PersonRoles(models.TextChoices):
        ACTOR = "actor", _("actor")
        DIRECTOR = "director", _("director")
        WRITER = "writer", _("writer")

    film_work = models.ForeignKey(
        Filmwork,
        on_delete=models.CASCADE,
        db_index=False,
        verbose_name=_("film_work for person"),
    )
    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        db_index=False,
        verbose_name=_("person for film_work"),
    )
    role = models.CharField(_("role"), max_length=255, choices=PersonRoles.choices)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "person_film_work"
        verbose_name = _("person of filmwork")
        verbose_name_plural = _("persons of filmwork")
        constraints = (
            models.UniqueConstraint(
                fields=(
                    "person",
                    "role",
                    "film_work",
                ),
                name="film_work_person_role",
            ),
        )

    def __str__(self):
        return ""

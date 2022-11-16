CREATE SCHEMA IF NOT EXISTS content;

CREATE TABLE IF NOT EXISTS content.film_work (
    id uuid PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    creation_date DATE,
    rating FLOAT,
    type VARCHAR(255) NOT NULL,
    created timestamp with time zone,
    modified timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.genre (
    id uuid PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created timestamp with time zone,
    modified timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.person (
    id uuid PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    created timestamp with time zone,
    modified timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.genre_film_work (
    id uuid PRIMARY KEY,
    genre_id uuid REFERENCES content.genre(id),
    film_work_id uuid REFERENCES content.film_work(id),
    created timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.person_film_work (
    id uuid PRIMARY KEY,
    person_id uuid REFERENCES content.person(id),
    film_work_id uuid REFERENCES content.film_work(id),
    role VARCHAR(255) NOT NULL,
    created timestamp with time zone
);

CREATE UNIQUE INDEX film_work_genre_ids
    ON content.genre_film_work (film_work_id, genre_id);

CREATE UNIQUE INDEX film_work_person_role_ids
    ON content.person_film_work (film_work_id, person_id, role);

CREATE INDEX person_id ON content.person_film_work (person_id);

CREATE INDEX genre_id ON content.genre_film_work (genre_id);

CREATE INDEX film_work_title ON content.film_work (title);

CREATE INDEX film_work_creation_date ON content.film_work (creation_date);

CREATE INDEX film_work_rating ON content.film_work (rating);

CREATE INDEX genre_name ON content.genre (name);

CREATE INDEX person_full_name ON content.person (full_name);

CREATE INDEX film_work_modified ON content.film_work (modified);

CREATE INDEX person_modified ON content.person (modified);

CREATE INDEX genre_modified ON content.genre (modified);
# Rayanesh Publication API

Rayanesh is the student publication of the Computer Engineering department at Sharif University of Technology. It releases magazine issues as PDFs, records podcasts, runs a blog and keeps a photo archive of its events. This repository is the Django REST Framework service behind the publication's website. It stores that content, exposes it as a read-mostly JSON API, and handles reader accounts.

I built the backend with [Hasti Karimi](https://github.com/HastiKarimi). [Arash Yadegari](https://github.com/Arash1381-y) built the React client that consumes this API.

## The problem

A volunteer editorial team publishes four different kinds of thing: PDF issues, audio episodes, written posts and event photos. Each one carries its own metadata (page count for an issue, duration for a podcast, photographer for a gallery image), but readers want to browse all of them the same way: by subject, by author, by year, most read first.

The team has nobody on call. So the API had to be something a non-engineer could fill from Django admin, the filtering had to be declarative rather than hand-written query code, and the whole stack (web, database, cache, worker) had to come up with one command on whatever laptop the next volunteer inherits.

## What it does

* Serves four content types over a versioned JSON API: issues, podcasts, blog posts and gallery photos.
* Serves the editorial team roster, with a flag for who appears on the landing page.
* Filters and orders list endpoints from query string parameters, including partial-text matching on names and subjects, date ranges, year-only matching, and sorting by read count.
* Counts reads. Every detail endpoint increments a `views_count` on the record it returns, which is also the field the `ordering` filter sorts on.
* Paginates lists at ten items per page.
* Accepts file uploads for issue PDFs, podcast audio, cover images and gallery photos, and serves them back under `/media/`.
* Handles registration with an email activation token, profile read and edit, password change and reset, and a soft account delete that flips `is_active` instead of dropping rows.
* Gives editors a Django admin for every content model, so publishing needs no custom CMS.

## API surface

Everything sits under `/v1/`. Content endpoints are open; the account endpoints noted below need a session.

| Method | Path | What it returns |
| --- | --- | --- |
| GET | `/v1/issue/` | Paginated, filterable list of magazine issues |
| GET | `/v1/issue/<id>/` | One issue, and increments its read count |
| GET | `/v1/podcast/` | Paginated, filterable list of episodes |
| GET | `/v1/podcast/<id>/` | One episode, and increments its read count |
| GET | `/v1/blog/` | Paginated, filterable list of posts |
| GET | `/v1/blog/<id>/` | One post, and increments its read count |
| POST | `/v1/blog/create/` | Creates a post from a JSON body |
| GET | `/v1/gallery/` | Paginated list of gallery photos |
| GET | `/v1/gallery/<id>/` | One photo, and increments its read count |
| GET | `/v1/staff/` | Editorial team roster |
| POST | `/v1/accounts/register/` | Creates an inactive user and mints an activation token |
| GET | `/v1/accounts/activate/<uidb64>/<token>/` | Activates the account and signs the user in |
| GET | `/v1/accounts/profile/` | Current profile (session required) |
| POST | `/v1/accounts/profile/edit/` | Updates first name, last name and email (session required) |
| POST | `/v1/accounts/profile/delete/` | Soft delete, sets `is_active` to false (session required) |
| GET | `/v1/accounts/profile/get?id=<id>` | Looks up a username by user id |
| GET, POST | `/v1/accounts/password_change/` | Django's password change view with a styled form |
| GET, POST | `/v1/accounts/password_reset/` | Django's reset view, which checks the address exists first |
| GET, POST | `/v1/accounts/password_reset_confirm/<uidb64>/<token>` | Sets the new password |
| any | `/admin/` | Django admin |

### Filtering

The `issue`, `podcast` and `blog` list endpoints accept query parameters defined in [`filters.py`](filters.py):

| Parameter | Applies to | Behaviour |
| --- | --- | --- |
| `name` | issue, podcast | Case-insensitive substring match |
| `subject` | podcast, blog | Case-insensitive substring match |
| `contributor` | blog | Case-insensitive substring match against the contributors text |
| `publishing_date__gte`, `publishing_date__lte` | issue, podcast | Inclusive date range |
| `posting_date__gte`, `posting_date__lte` | blog | Inclusive date range |
| `publishing_date__year`, `posting_date__year` | respective model | Year-only match |
| `ordering` | all three | `ascending` or `descending`, sorted by `views_count` |
| `page` | all lists | Page number, ten items per page |

Example:

```
GET /v1/blog/?subject=compiler&posting_date__year=2023&ordering=descending&page=2
```

That returns the second page of 2023 posts whose subject contains "compiler", most read first.

## Data model

Every content model extends `TimeStampedModel` from `django-model-utils`, so `created` and `modified` come for free and are excluded from the public filter surface.

| Model | App | Fields worth knowing |
| --- | --- | --- |
| `Issue` | `issue` | `raw_file` (the PDF), `cover_image`, `name`, `authors`, `subject`, `pages_number`, `publishing_date`, `is_issue`, `views_count` |
| `Podcast` | `podcast` | `raw_file` (audio), `cover_image`, `name`, `contributors`, `subject`, `length` as a `DurationField`, `publishing_date`, `views_count` |
| `BlogPost` | `blog` | `post_content` as a `JSONField`, `contributors`, `subject` (unique), `reading_time`, `posting_date`, `views_count`, `preview` |
| `GalleryPhoto` | `gallery` | `image`, `caption`, `attenders`, `photographer`, `shooting_date`, `publishing_date`, `views_count` |
| `Staff` | `staff` | `first_name`, `last_name`, `position`, `image`, `present_in_landing_page` |

Two choices here are worth calling out. Blog posts store their body as JSON rather than HTML or Markdown, so the React client renders a block structure (headings, paragraphs, code, images) instead of trusting raw markup typed by an editor. And author and contributor lists are free text with a comma or newline separator rather than a join table, which was the right trade for a team of a dozen people where the same name gets spelled three ways.

The `accounts` app defines no model of its own. It uses `django.contrib.auth.models.User` and adds the forms, the activation token generator and the views around them.

## Technologies

* **Django 4.1** and **Django REST Framework 3.13** for the API
* **PostgreSQL** through `psycopg2` for storage
* **Redis** as the Celery broker and result backend
* **Celery 5.2** with `django-celery-results` for background work
* **django-filter** for the declarative query parameters above
* **django-model-utils** for timestamped base models
* **django-cors-headers**, scoped to the React dev server on port 3000
* **Pillow** for image field handling
* **Docker** and **Docker Compose** for the four-container local stack

## Running it

### With Docker Compose

This brings up PostgreSQL, Redis, the Django server and a Celery worker together.

```bash
git clone https://github.com/Imanm02/Rayanesh-Django-Backend.git
cd Rayanesh-Django-Backend
./run.sh
```

`run.sh` wraps `sudo docker-compose build` and `sudo docker-compose up --remove-orphans`. It hardcodes `sudo`, which you do not want on macOS or Windows, so run the two commands directly there:

```bash
docker compose build
docker compose up --remove-orphans
```

The API then answers on `http://localhost:8000/`, PostgreSQL on 5432 and Redis on 6379. The web container runs `makemigrations` and `migrate` on start, so the schema is created on first boot.

Set the database credentials before the first run. `docker-compose.yml` ships placeholder values for `POSTGRES_DB`, `POSTGRES_USER` and `POSTGRES_PASSWORD` on both the `rayanesh_postgres` and `rayanesh` services, and the same values have to be reflected in the `DATABASES` block in `RayaneshBackend/settings.py`, with `HOST` switched to `rayanesh_postgres`.

### Without Docker

You need Python 3.8 or later, a running PostgreSQL, and a running Redis if you want the worker.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install six                    # imported by accounts/tokens.py, missing from requirements.txt

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The default `DATABASES` block points at `127.0.0.1:5432`. Edit it to match your local PostgreSQL, or uncomment the SQLite block just above it if you only want to poke at the API.

To run the worker in a second shell:

```bash
celery -A RayaneshBackend worker -l INFO
```

Then open `http://localhost:8000/admin/` to add content, and call the endpoints above.

## Configuration

Settings currently live in `RayaneshBackend/settings.py` as literals. If you deploy this, move at minimum `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, the `DATABASES` credentials and the Celery URLs into environment variables. The checked-in `SECRET_KEY` is the `django-insecure-` one that `django-admin startproject` generates, `DEBUG` is `True`, and the database password is a placeholder. None of that is safe outside a development machine.

Settings that matter beyond the defaults:

* `CORS_ALLOWED_ORIGINS` allows `http://localhost:3000`, the Create React App dev server.
* `REST_FRAMEWORK` sets page size 10 and `PageNumberPagination` as the default.
* `MEDIA_ROOT` is `media/` at the project root, and the root URLconf serves it directly, which works under `DEBUG` but needs a real static file server in production.
* `EMAIL_BACKEND` is the console backend, so activation and reset mail prints to the terminal instead of being sent.

## Project structure

```
RayaneshBackend/     Project package: settings, root URLconf, WSGI/ASGI, Celery app
  celery.py          Celery app, reads CELERY_* settings, autodiscovers tasks
  middlewares.py     Minimal pass-through middleware
accounts/            Registration, activation tokens, profile, password forms
issue/               Magazine issues: model, serializer, list and detail views
podcast/             Audio episodes, same shape as issue
blog/                Posts with JSON bodies, plus a create endpoint and its own paginator
gallery/             Event photos
staff/               Editorial roster, list only
filters.py           All three FilterSets in one module at the project root
Dockerfile           Python 3.8 image, installs requirements, drops to a non-root user
docker-compose.yml   postgres, redis, web and celery worker
run.sh               Build and up
```

Each content app follows the same four-file pattern: `models.py`, `serializers.py`, `views.py`, `urls.py`. Lists are DRF `ListAPIView`, details are a plain `APIView` because they perform a write (the read counter) before serializing. Filters are the one thing that does not follow the per-app pattern. All three FilterSets sit in a single root-level `filters.py` so that the near-identical date and ordering logic stays in one place instead of drifting apart across apps.

## Implementation details

**Read counting.** A detail view is not a pure read. `IssueDetail.get`, `PodcastDetail.get`, `BlogPostDetail.get` and `GalleryDetail.get` each load the object, increment `views_count`, save, then serialize. That is why detail views are `APIView` rather than `RetrieveAPIView`. The counter is also what the `ordering` filter sorts on, so "most read" needs no separate analytics store.

**Shared ordering filter.** All three FilterSets expose `ordering` as a `ChoiceFilter` whose `filter_by_order` method maps `ascending` and `descending` onto `views_count` and `-views_count`. The `Meta.exclude` lists keep file fields and timestamps out of the generated filter form, so the query surface stays small even though the models are wide.

**Account activation.** `accounts/tokens.py` subclasses `PasswordResetTokenGenerator` and folds `user.is_active` into the hash value. Once the user activates, the hash input changes and the token stops validating, so an activation link cannot be replayed. Registration saves the user with `is_active=False` and builds a base64 uid plus token pair; the activate view decodes them, checks the token, flips the flag and logs the user in.

**Soft delete.** `delete_user` sets `is_active` to false instead of deleting the row, which keeps authorship on already published posts intact.

**Celery wiring.** `RayaneshBackend/celery.py` creates the app, pulls `CELERY_*` settings from Django and calls `autodiscover_tasks()`. Compose runs a worker container against Redis. No task modules are defined in this repository yet, so the worker starts and idles; the plumbing is there for the digest mail and PDF thumbnailing that were planned next.

**Container hygiene.** The Dockerfile creates a `web` user with uid 1000 and switches to it before the image is used, so the container does not run as root.

## Known rough edges

I would rather list these than pretend they are not there.

* `SECRET_KEY`, the database name, user and password are hardcoded in `settings.py`, and `DEBUG` is `True`. See [Configuration](#configuration).
* Migration files are not committed. The containers run `makemigrations` on start, which works against a fresh database but means migration history is not reproducible across environments. Generating and committing them is the fix.
* `/v1/accounts/login/` points at a name that resolves to Django's `django.contrib.auth.login` helper rather than a view, because the project's own login view is commented out in `accounts/views.py`. That route does not work. Session login through `/admin/` does.
* `IssueFilter.subject` is declared as a `ChoiceFilter` with no `choices`, so `?subject=` on `/v1/issue/` rejects every value. It should be a `CharFilter` like the podcast and blog equivalents.
* The activation route pattern in `accounts/urls.py` carries a stray `)` after the token segment, so real activation links have to match it literally.
* Several `accounts` endpoints still return placeholder JSON bodies, left over from the move away from server-rendered templates toward a React client. `post_search` in the same module references names that are never imported and is not routed.
* `django-bootstrap4`, `django-tables2` and `Faker` are installed but unused now that the templates are gone. `six` is imported by `accounts/tokens.py` but is missing from `requirements.txt`.
* `CommonMiddleware` appears twice in the `MIDDLEWARE` list, and `STATIC_ROOT` is built with `BASE_DIR.joinpath('/static')`, which resolves to an absolute `/static` rather than a path under the project.
* There are no tests. Every `tests.py` is the empty stub that `startapp` writes.

## Screenshots and design

[`Rayanesh Presentation.pdf`](Rayanesh%20Presentation.pdf) walks through the finished product: the Figma desktop and mobile designs, the landing page, the blog reader, the issue archive, and the sign-in and registration screens as they were built. The interface is Persian and right to left, which is why the frontend ships the Vazir and BArshia typefaces.

## Background

This began as a team project in a web programming course at Sharif University of Technology in late 2022, built for the CE department's actual student publication rather than as an exercise. The API shape, the read counters and the JSON blog bodies all came from what the editorial team asked for.

## Credits

* [Iman Mohammadi](https://github.com/Imanm02), backend
* [Hasti Karimi](https://github.com/HastiKarimi), backend
* [Arash Yadegari](https://github.com/Arash1381-y), frontend

## License

MIT. See [LICENSE](LICENSE).

# Shared Blog App

Reusable Django app for all Yatuk projects.

## Features
- Multilingual category, tag and post fields (`en`, `ru`, `hy`)
- Explicit table names (`blog_category`, `blog_tag`, `blog_post`)
- Admin integration
- Public list/detail routes

## Migration Owner Pattern
Use `cms` as migration owner for this app.

1. Run blog migrations only from `cms`:
   - `cd cms`
   - `python manage.py migrate blog`
2. In other projects, do not run broad `migrate` commands that may change schema unexpectedly.
3. Keep one source of truth for blog migrations in this folder.

## URLs
- `/blog/`
- `/blog/<slug>/`

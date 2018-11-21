Investment Wizard Web Application
========

This is a web application prototype for EMSF capstone project. It will be demostrating some basic functionalities requested by the user as part of the overarching objective.
Flask, Jinja, and MongoDB are used to fulfill the requirements.

The application requires MongoDB to be running without authentication enabled.

Once this is running, execute the app and navigate to the endpoint (default: `http://127.0.0.1:4995/`).

The available endpoints are:

- `/`
- `/login`
- `/register`
- `/blogs`
- `/blogs/new`
- `/posts/<string:blog_id>`
- `/posts/new/<string:blog_id>`

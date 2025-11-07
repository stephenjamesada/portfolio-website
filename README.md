# My Portfolio Site

## Tech Stack

- Raw HTML/CSS/JS (no frameworks)
- Flask

Flask is doing most of the heavy lifting. There is no JS in the site that actually contributes to the site's interactivity and functionality; it's just for what's inside the console, so Flask handles what you'd expect JS to.

As I'm new to Flask development, I added a [`base.html`](./templates/base.html) rather late, so all pages made prior to [`projects.html`](./templates/projects.html) were handled with raw HTML rather than Jinja2 syntax.

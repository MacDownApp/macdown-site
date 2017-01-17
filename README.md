# Source files for macdown.uranusjr.com

These are [Lektor] source files used to generate <macdown.uranusjr.com>. The generated files are hosted on Netlify with the custom domain name.

## Run site locally

1. Install [Lektor].
2. Install Python dependencies: `pip install requirements.txt`.
2. Optional: Install [pyobjc-framework-webkit] for faster JavaScript server-side rendering.
3. `invoke build` to build the files. Internet connection is required on the first run.
4. `invoke server` to launch the dev server.
5. Visit `http://localhost:5000`.


## TODO

Deployment:

* Route <macdown.uranusjr.com> to the current site.
* Make sure update-pushing works.
* Enable HTTPS on Netlify.
* Switch feed URL in MacDown to use HTTPS.
* Add a license file to the repo.

Feature:

* Re-write release script in the main repo to integrate with the JSON publish API.

Markdown renderer:

* Escape in math blocks.
* Quote syntax.


[Lektor]: https://www.getlektor.com
[pyobjc-framework-webkit]: http://pythonhosted.org/pyobjc-framework-WebKit/

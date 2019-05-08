# Source files for the official MacDown site

These are [Lektor] source files used to generate <http://macdown.uranusjr.com>. The generated files are hosted on Netlify with the custom domain name.

## Run site locally

1. Install [Lektor].
2. Install Python dependencies: `pip install -r requirements.txt`.
2. Optional: Install [pyobjc-framework-webkit] for faster JavaScript server-side rendering.
3. `invoke build` to build the files. Internet connection is required on the first run.
4. `invoke serve` to launch the dev server.
5. Visit `http://localhost:5000`.


## TODO

Deployment:

* Make sure update-pushing works.
* Add a license file to the repo.

Feature:

* Re-write release script in the main repo to integrate with the JSON publish API.

Markdown renderer:

* `$`-style math.
* Context-aware `$$` math.
* Escape in math syntax.
* Quote syntax.


[Lektor]: https://www.getlektor.com
[pyobjc-framework-webkit]: http://pythonhosted.org/pyobjc-framework-WebKit/

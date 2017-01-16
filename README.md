# Source files for macdown.uranusjr.com

These are [Lektor] source files used to generate <macdown.uranusjr.com>. The generated files are hosted on Netlify with the custom domain name.

## Run site locally

1. Install [Lektor].
2. Add either [pyobjc-framework-webkit] or [PyMiniRacer] to the Python installation.
3. `lektor build` to build the files. Internet connection is required on the first run.
4. `lektor server` to launch the dev server.
5. Visit `http://localhost:5000`.


## TODO

Deployment:

* Route <macdown.uranusjr.com> to the current site.
* Make sure update-pushing works.
* Enable HTTPS on Netlify.
* Switch feed URL in MacDown to use HTTPS.

Feature:

* Script to generate new release file from a MacDown build.

Markdown renderer:

* Inline math is hoisted to the brginning of a text group.
* Escape in math blocks.
* Quote syntax.


[Lektor]: https://www.getlektor.com
[pyobjc-framework-webkit]: http://pythonhosted.org/pyobjc-framework-WebKit/
[PyMiniRacer]: https://github.com/sqreen/PyMiniRacer

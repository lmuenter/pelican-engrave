# Engrave: QR Codes for Pages and Articles

[![Build Status](https://img.shields.io/github/actions/workflow/status/pelican-plugins/engrave/main.yml?branch=main)](https://github.com/lmuenter/pelican-engrave/actions)
[![PyPI Version](https://img.shields.io/pypi/v/pelican-engrave)](https://pypi.org/project/pelican-engrave/)
[![Downloads](https://img.shields.io/pypi/dm/pelican-engrave)](https://pypi.org/project/pelican-engrave/)
![License](https://img.shields.io/pypi/l/pelican-engrave?color=blue)

**Engrave** is a Pelican plugin that generates QR codes for the URLs of your blog posts and pages, providing quick access to your content on mobile devices by scanning the code.

## Installation

This plugin can be installed via:

```bash
python -m pip install pelican-engrave
```

As long as you have not explicitly added a `PLUGINS` setting to your Pelican settings file, then the newly-installed plugin should be automatically detected and enabled. Otherwise, you must add `engrave` to your existing `PLUGINS` list. For more information, please see the [How to Use Plugins](https://docs.getpelican.com/en/latest/plugins.html#how-to-use-plugins) documentation.

## Usage

Engrave automatically generates QR codes for all articles and pages in your Pelican site. These QR codes are saved as SVG images in the `engrave/` directory within the `OUTPUT_PATH` defined in your Pelican settings.

### Accessing QR Codes in Templates

The generated QR code is available in the context of the content as `content.engrave_qrcode`. You can embed the QR code in your templates using the following syntax:

```html
<img src="{{ content.engrave_qrcode }}">
```

### Engrave Directory Cleanup

Before generating new QR codes, Engrave clears the `engrave/` directory to ensure that no legacy QR codes remain. This aims at maintaining security and consistency. Only by latest codes are available this way.

### Schema Validation

Engrave validates URL schemas to ensure security. By default, it only allows URLs with the `https` schema. If your site uses another schema (e.g., `http` or `ftp`), you need to explicitly add it to the allowed schemas in your Pelican settings.

### Setting Allowed Schemas

To specify which URL schemas are allowed for QR code generation, use the `ENGRAVE_ALLOWED_SCHEMES` setting in your Pelican configuration file (`pelicanconf.py`). For example:

```python
ENGRAVE_ALLOWED_SCHEMES = ["https", "http"]
```

### Required Settings

- **SITEURL**: Ensure that `SITEURL` is set in your Pelican configuration file. This setting is crucial as it forms the basis of the URLs used for QR code generation. Be sure to synchronize `ENGRAVE_ALLOWED_SCHEMES` with your `SITEURL` setting to avoid any discrepancies.

## Contributing

Contributions are welcome and much appreciated. Every little bit helps. You can contribute by improving the documentation, adding missing features, and fixing bugs. You can also help out by reviewing and commenting on [existing issues][].

To start contributing to this plugin, review the [Contributing to Pelican][] documentation, beginning with the **Contributing Code** section.

[existing issues]: https://github.com/lmuenter/pelican-engrave/issues
[Contributing to Pelican]: https://docs.getpelican.com/en/latest/contribute.html

### Development

To set up a development environment for Engrave, follow these steps.

1. Create and activate the venv:
```
python -m venv venv
source venv/bin/activate
```

2. Install dependencies
```
python -m pip install -r requirements.txt
```


## License

This project is licensed under the MIT license.

from string import Formatter


class SuperFormatter(Formatter):

    """
    SuperFormatter adds the following capabilities:

    1. Initialize with a template string, and the __call__ method uses
       this string.  Thus, example usage of this formatter looks like,

          template = SuperFormatter(template_string)
          out_string = template(*args, **kwargs)

    2. White space at the end of a format specifier is stripped. This
       allows for aligning text more easily.

    3. Multiple format strings separated by '|' are supported. This
       formatter will loop over the format strings until it finds one
       that doesn't throw a ValueError.  For example the format string
       '6d|<6.3f|8s' will format the following objects as:

           |    input    |   output string  |
           +-------------+------------------+
           | 3.74583754  |      '3.746 '    |
           |     384     |      '   384'    |
           |    None     |    'None    '    |

    4. Default values may be specified after a '/' at the end of the
       format string. For example if the container is
       '{show_data:s/False}', and there is no key 'show_data' in
       **kwargs, then 'False' will fill that location.

    5. The 'format_prfx' specifier allows the user to define a default
       container prefix.  This will be prepended to all format
       specifiers that are a single-character 'type' specifier.  For
       example if `format_prfx = '<20'`, then the format specifier 'f'
       will be changed to '<20f', but '>08.3f' will be unchanged.
       This is applied to each specifier within a multiple
       specification, thus 'd|f|s' would actually be '<20d|<20f|<20s'.

    6. Custom format specifiers have been implemented by adding a
       hook that searches for a `_format_<specifier>` method prior to
       running the normal formatting routines.  That method takes the
       value to be formatted as input (in addition to *self*), and
       should return the fully-formatted string (no further formatting
       is applied).

       Thus, a custom format specifier 'pet' (which might be specified
       as {my_dog:pet} in the template) could be defined by:

       class MyNewFormatter(SuperFormatter):

           def _format_pet(self, value):
               return value.upper()

       Note that this will throw an AttributeError if *my_dog* is an
       object without an 'upper' method (i.e. not a string), but you
       could add to the method to handle all of the different types
       that value might be.

    """

    format_prfx = ''

    def __init__(self, template):
        # Override the base methods to initialize the formatter with
        # the template string.
        self.template = template

    def __call__(self, *args, **kwargs):
        return self.format(self.template, *args, **kwargs)

    def __iter__(self,):
        return self.parse(self.template)

    def get_value(self, key, args, kwargs):
        key = key.rstrip()
        self._current_name = key
        if isinstance(key, (int, long)):
            return args[key]
        else:
            try:
                return kwargs[key]
            except KeyError:
                return None

    def format_field(self, value, format_spec):
        format_spec = format_spec.rstrip()  # Strip trailing spaces

        if '/' in format_spec:
            format_spec, default_val = format_spec.split('/')
            # set the default value if there is no input
            if value is None:
                return format(default_val,
                              self.format_prfx + 's')
        elif value is None:
            raise KeyError("'%s' not specified and no default value found in template." % self._current_name)  # noqa

        if '|' in format_spec:
            format_spec = format_spec.split('|')
        else:
            format_spec = [format_spec]
        for form in format_spec:
            try:
                if hasattr(self, '_format_' + form):
                    return getattr(self, '_format_' + form)(value)
                if form in ["b", "c", "d", "e", "E",
                            "f", "F", "g", "G", "n",
                            "o", "s", "x", "X", "%", '']:
                    form = self.format_prfx + form
                return format(value, form)
            except ValueError:
                pass
        raise ValueError('Invalid conversion specification')

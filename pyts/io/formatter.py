from string import Formatter


class SuperFormatter(Formatter):

    r"""
    SuperFormatter adds the following capabilities:

    1. Initialize with a template string, and the :meth:`__call__` method uses
       this string.  Thus, example usage of this formatter looks like::

          template = SuperFormatter(template_string)
          out_string = template(*args, **kwargs)

    2. White space at the end of a format specifier is stripped. This
       allows for aligning text within the template.

    3. Multiple format strings separated by ``|`` can be specified
       within a template. This formatter will loop over the format
       strings until it finds one that doesn't throw a ValueError.
       For example, the format string ``6d|<6.3f|8s`` will format the
       following objects as:

           +----------------+------------------+
           |    input       |   output string  |
           +================+==================+
           | ``3.74583754`` |    ``'3.746 '``  |
           +----------------+------------------+
           |     ``384``    |  ``'   384'``    |
           +----------------+------------------+
           |    ``None``    |    ``'None    '``|
           +----------------+------------------+

    4. Default values may be specified after a ``/`` at the end of the
       format string. For example if the container is
       ``{show_data:s/False}``, and there is no key ``show_data`` in
       ``**kwargs``, then ``False`` will fill that location.

    5. The :attr:`format_prfx` attribute allows the user to define a
       default container prefix.  This will be prepended to all format
       specifiers that are a single-character `type` specifier.  For
       example if ``format_prfx = '<20'``, then the format specifier
       ``'f'`` will be changed to ``'<20f'``, but ``'>08.3f'`` will be
       unchanged.  This is applied to each specifier within a multiple
       specification, thus ``'d|f|s'`` would actually be
       ``'<20d|<20f|<20s'``.

    6. Custom format specifiers have been implemented by adding a
       hook that searches for a `_format_<specifier>` method prior to
       running the normal formatting routines.  That method takes the
       value to be formatted as input (in addition to *self*), and
       should return the fully-formatted string (no further formatting
       is applied).

       For example, a custom format specifier `pet` (specified as
       ``{my_dog:pet}`` in the template) could be defined as::

           class MyNewFormatter(SuperFormatter):

               def _format_pet(self, value):
                   return value.upper()

       Note that this will throw an ``AttributeError`` if *my_dog* is an
       object without an ``upper`` method (i.e. not a string), but you
       could add to the method to handle all of the different types
       that ``value`` might be.

    7. Custom format specifiers with arguments can be specified as
       ``{my_dogs:pets(10s,10s)}``. In this case the string inside
       the parenthesis is supplied as the second argument to the
       ``_format_pets`` method.  The method that implements this
       format could be defined as::

           class MyNewFormatter(SuperFormatter):

               def _format_pets(self, value, form2):
                   out = ''
                   for v,f in zip(value, form2.split(',')):
                       out += format(v, f)
                   return out


    """

    format_prfx = ''
    default_format_prfx = ''
    allow_sloppy = False

    def __init__(self, template):
        # Override the base methods to initialize the formatter with
        # the template string.
        self.template = template

    def __call__(self, *args, **kwargs):
        r"""
        Format the template string with `*args` and `**kwargs`.
        """
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

    def _fail(self):
        if self.allow_sloppy:
            return '??SOME JUNK??'
        else:
            # This _current_name business is a DIRTY HACK.
            raise KeyError("'%s' not specified and no default "
                           "value found in template." % self._current_name)

    def _format_default(self, default_val):
        return format(default_val, self.default_format_prfx + 's')

    def format_field(self, value, format_spec):
        format_spec = format_spec.rstrip()  # Strip trailing spaces
        default_val = None
        if '/' in format_spec:
            format_spec, default_val = format_spec.split('/', 1)
            # set the default value if there is no input
            if value is None:
                return self._format_default(default_val)
        elif value is None:
            return self._fail()

        if '|' in format_spec:
            format_spec = format_spec.split('|')
        else:
            format_spec = [format_spec]
        for form in format_spec:
            formtail = None
            if '(' in form and form.endswith(')'):
                form, formtail = form.split('(', 1)
                formtail = formtail[:-1]

            try:
                if hasattr(self, '_format_' + form):
                    if formtail is None:
                        return getattr(self, '_format_' + form)(value)
                    else:
                        return getattr(self, '_format_' + form)(value,
                                                                formtail)
                if form in ["b", "c", "d", "e", "E",
                            "f", "F", "g", "G", "n",
                            "o", "s", "x", "X", "%", '']:
                    form = self.format_prfx + form
                return format(value, form)
            except ValueError:
                pass
            except TypeError:
                pass
        # Finally, try the default again:
        if default_val is None:
            raise ValueError('Invalid conversion specification')
        return self._format_default(default_val)

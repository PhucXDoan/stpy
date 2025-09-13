from ..stpy.database import system_properties, system_locations
from ..pxd.log       import log, ANSI
from ..pxd.utils     import justify



################################################################################



def stringify_table(items):

    return '\n' + '\n'.join(
        '| {} | {} |'.format(*justs)
        for justs in justify(
            (
                ('<', key),
                ('>', f'{value :,}' if isinstance(value, (int, float)) else repr(value)),
            )
            for key, value in items
        )
    ) + '\n'



def get_similars(given, options): # TODO Copy-pasta.

    import difflib

    return difflib.get_close_matches(
        given if given is not None else 'None',
        [option if option is not None else 'None' for option in options],
        n      = 3,
        cutoff = 0
    )



################################################################################



class SystemPlanner:

    def __init__(self, target):

        self.target     = target
        self.dictionary = {}
        self.draft      = None
        self.used_keys  = []



    # Prevent keys already in the planner from being overwritten.

    def __setitem__(self, key, value):

        if key in self.dictionary:
            raise RuntimeError(
                f'Key {repr(key)} is already defined in the '
                f'clock-tree planner for target {repr(self.target.name)}.'
            )

        if self.draft is None:
            self.dictionary[key] = value
        else:
            self.draft[key] = value



    # Ensure keys into the planner exists.
    # We also keep track of all keys used
    # so we can warn on any unused keys.

    def __getitem__(self, key):

        if self.draft is not None and key in self.draft:
            return self.draft[key]

        if key not in self.dictionary:
            raise RuntimeError(
                f'No key {repr(key)} '
                f'found in the clock-tree planner '
                f'for target {repr(self.target.name)}; '
                f'closest matches are: '
                f'{get_similars(key, self.dictionary)}.'
            )

        if key not in self.used_keys:
            self.used_keys += [key]

        return self.dictionary[key]



    # Allow for easy print-debugging.

    def __str__(self):
        return stringify_table(self.dictionary.items())



    # Create a peripheral-register-field-value tuple,
    # typically for register reads and writes.

    def tuple(self, key, value = ...):

        if value is ...:
            value = self[key]

        return (*system_locations[self.target.mcu][key], value)



    # Nothing particular interesting to say here
    # after parameterization for the planner...

    def done_parameterize(self):

        self.used_keys = []



    # Ensure we have used all planner values.

    def done_configurize(self):

        if unused_keys := [
            key
            for key, value in self.dictionary.items()
            if key not in self.used_keys
            if value is not None
        ]:
            log(ANSI(
                f'[WARNING] There are unused {self.target.mcu} planner keys: {unused_keys}.',
                'fg_yellow'
            ))

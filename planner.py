from ..stpy.database import system_database
from ..pxd.log       import log, ANSI



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



def get_similars(given, options):

    import difflib

    return difflib.get_close_matches(
        given if given is not None else 'None',
        options,
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
                f'clock-tree plan for target {repr(self.target.name)}.'
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
                f'found in the clock-tree plan '
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



    # We can enter a state of brute-forcing where we will be
    # creating key-value pairs, but they won't be finalized until
    # the end of the brute-forcing, if successful at all.

    def brute(self, function):

        self.draft = {}

        success = function()

        if not success:
            raise RuntimeError(
                f'Could not brute-force configurations '
                f'that satisfies the system parameterization.'
            )

        self.dictionary |= self.draft
        self.draft       = None



    # Create a peripheral-register-field-value tuple,
    # typically for register reads and writes.

    def tuple(self, key, value = ...):

        if value is ...:
            value = self[key]

        entry = system_database[self.target.mcu][key]

        return (entry.peripheral, entry.register, entry.field, value)



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
                f'[WARNING] There are unused {self.target.mcu} plan keys: {unused_keys}.',
                'fg_yellow'
            ))

import stevedore
import logging

from pypif.obj import System


def _callback(manager, entrypoint, exception):
    """Log errors in loading extensions as warnings"""
    logging.warning("Failed to load '{}' due to {}".format(entrypoint, exception))
    return


class IngesterManager:
    """Load ingest extensions and invoke them on demand"""

    def __init__(self):
        self.extension_manager = stevedore.extension.ExtensionManager(
            namespace='citrine.dice.converter',
            invoke_on_load=False,
            on_load_failure_callback=_callback
        )

    def run_extension(self, name, path, args):
        """Run extension by name on path with arguments"""
        if name in self.extension_manager:
            extension = self.extension_manager[name]
            pifs = extension.plugin.convert([path], **args)
            return pifs
        else:
            logging.error("{} is an unknown format\nAvailable formats: {}".format(name, self.extension_manager.names()))
            exit(1)

    def run_extensions(self, files, args={}, include=None, exclude=[]):
        """Run any extensions in include but not exclude

        Returns list of pifs converted.
        """
        if not include:
            include = self.extension_manager.entry_points_names()
        include = [x for x in include if x in self.extension_manager and x not in exclude]

        for name in include:
            extension = self.extension_manager[name]
            try:
                pifs = extension.plugin.convert(files, **args)
                # Return value from convert can be System, list of Systems, or generator
                if isinstance(pifs, System):
                    pifs = [pifs]
                else:
                    pifs = [p for p in pifs]
                # TODO: make this selection logic smarter
                if len(pifs) > 0:
                    return pifs
            except:
                pass
        logging.warning("None of these ingesters worked: {}".format(include))
        return []

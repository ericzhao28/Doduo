"""
Doduo/Doduo.matcher

Compiles pattern blueprints from `Doduo/configs/` and handles
all query matching requests.
"""

from yaml import load, YAMLError

from Doduo.query import parse_query
from Doduo.template import Template
from Doduo.config import ROOT_DIR
from Doduo import ConfigException, InvalidUsage


class Matcher:
    """
    Singleton class instantiated once by the Flask server.
    Loads in all relevant blueprints from the provided config file
    and stores them in Matcher.templates. The Matcher class
    provides a match(...) function to query against the compiled
    templates.
    """

    def __init__(self, config_file=None):
        """
        Args:
            config_file (str): Config file to locate template blueprints in.
                               If None, no templates will be loaded.
        Returns:
            None
        """
        # By default, allow Matcher to be created with no preloaded templates.
        if config_file is None:
            self.templates = {}
            return

        # Attempt to load in and parse the Yaml config.
        try:
            with open(ROOT_DIR + "configs/" + config_file, "r") as f:
                self.config = load(f)
        except (YAMLError, FileNotFoundError) as exc:
            raise ConfigException(
                "Config file '{}' not found or invalid YAML.".format(
                    config_file
                )
            )

        # Build a map in self.templates from template_id's to
        # to lists (lists of compiled patterns).
        self.templates = {}
        for template_id, patterns in self.config.items():
            self.templates[template_id] = [
                self.build_template(blueprint)
                for blueprint in patterns["patterns"]
            ]

    def build_template(self, blueprint):
        """
        Build a template's blueprint into Template class tree.

        Args:
            blueprint (dict): deep parsed dict/list/str object parsed
                              from a YAML config.
        Returns:
            A deep Template tree composing the compiled blueprint.
        """
        template_args = dict(blueprint)

        # Compile the blueprints for each of the children.
        children = []
        if "children" in template_args:
            children = [
                self.build_template(child)
                for child in template_args["children"]
            ]
            template_args.pop("children")

        # Attempt to build the Template object for this level of the blueprint,
        # providing the compiled children to include in the tree's child list.
        try:
            new_template = Template(children=children, **template_args)
        except TypeError:
            raise ConfigException("Invalid config option provided.")

        return new_template

    def match(self, query, template_ids):
        """
        Match against query against potential templates.
        Args:
            query (str):         string to query against our templates.
            template_ids (list): list of strings specifying which templates
                                 to search through. If set to None, the
                                 search space will be all known templates.
        Returns:
            Generator of dictionaries. Each dictionary corresponds
            to results for a single sentence.
        """

        # Recursively attempt to match a pattern against each location
        # in the tree.
        def __match(parsed, pattern):
            slots = []
            result = pattern.match(parsed)
            if result is not False:
                slots += result
            for child in parsed.children:
                result = __match(child, pattern)
                if result is not False:
                    slots += result
            return slots

        # Parse the list of template_ids. If template_ids is set,
        # limit our search space to those IDs. Otherwise, search
        # across all templates.
        if template_ids is None:
            templates = list(self.templates.items())
        else:
            templates = []
            for id in template_ids:
                try:
                    templates.append((id, self.templates[id]))
                except KeyError:
                    raise ConfigException(
                        "Provided template ID {} not in config.".format(id)
                    )

        # Parse the user query and catch any invalid `query` values.
        try:
            parsed_query = parse_query(query)
        except (TypeError, ValueError):
            raise InvalidUsage("Invalid query body.")

        for parsed, sentence in parsed_query:
            # Include metadata for this sentence's payload.
            results = {}
            results["__sentence__"] = sentence
            results["__alternatives__"] = {}

            for template_id, patterns in templates:
                # Build up a list of possible results
                # across each pattern for the given template.
                slots = []
                for t in patterns:
                    match_results = __match(parsed, t)
                    if match_results is not False:
                        slots += match_results

                # Split list of possible results into
                # "main" result and a set of alternatives.
                if slots:
                    results[template_id] = slots.pop(0)
                    if slots:
                        results["__alternatives__"][template_id] = slots

            yield results

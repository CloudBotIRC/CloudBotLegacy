import re
import random

TEMPLATE_RE = re.compile(r"\{(.+?)\}")


class TextGenerator(object):
    def __init__(self, templates, parts, default_templates=None, variables=None):
        self.templates = templates
        self.default_templates = default_templates
        self.parts = parts
        self.variables = variables

    def generate_string(self, template=None):
        """
        Generates one string using the specified templates.
        If no templates are specified, use a random template from the default_templates list.
        """
        # this is bad
        if self.default_templates:
            text = self.templates[template or random.choice(self.default_templates)]
        else:
            text = random.choice(self.templates)

        # replace static tags in the template with provided values
        
        # eg: if the template contains the tag {age} and you provide the variable age when creating the textgen,
        # instances of {age} will be replaced with the variable provided before the random stage
        if self.variables:
            for key, value in self.variables.items():
                text = text.replace("{%s}" % key, value)

        # get a list of all text parts we need
        required_parts = TEMPLATE_RE.findall(text)
        
        # TODO: replace the simple logic here with a system that can allow multiple instances of the
        # same tag to be handled
        
        # eg: if there are two instances of the tag {example} in the template, each one should be
        # replaced with a random part instead of both getting the same part

        for required_part in required_parts:
            ppart = self.parts[required_part]
            # check if the part is a single string or a list
            if not isinstance(ppart, basestring):
                part = random.choice(self.parts[required_part])
            else:
                part = self.parts[required_part]
            text = text.replace("{%s}" % required_part, part)

        return text

    def generate_strings(self, amount, template=None):
        strings = []
        for i in xrange(amount):
            strings.append(self.generate_string())
        return strings

    def get_template(self, template):
        return self.templates[template]

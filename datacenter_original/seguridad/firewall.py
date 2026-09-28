from seguridad.policies import SecurityPolicy


class Firewall:

    def __init__(self, name):

        self.name = name

        self.default_policy = "DENY"

        self.rules = []


    def add_rule(self, rule):

        if not isinstance(
            rule,
            SecurityPolicy
        ):

            raise TypeError(
                "rule must be a SecurityPolicy"
            )

        self.rules.append(rule)


    def check_connection(
        self,
        source_zone,
        destination_zone,
        protocol,
        port
    ):

        for rule in self.rules:

            if (
                rule.source_zone
                == source_zone
                and
                rule.destination_zone
                == destination_zone
                and
                rule.protocol
                == protocol
                and
                rule.port
                == port
            ):

                return rule.action

        return self.default_policy
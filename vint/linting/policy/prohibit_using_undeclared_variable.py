from vint.ast.node_type import NodeType
from vint.linting.level import Level
from vint.linting.policy.abstract_policy import AbstractPolicy
from vint.linting.policy_registry import register_policy
from vint.ast.plugin.scope_plugin import (
    is_reference_identifier,
    is_reachable_reference_identifier,
)


@register_policy
class ProhibitUsingUndeclaredVariable(AbstractPolicy):
    def __init__(self):
        super(ProhibitUsingUndeclaredVariable, self).__init__()
        self.description = 'Variable is not declared'
        self.reference = ':help E738'
        self.level = Level.WARNING


    def listen_node_types(self):
        return [NodeType.IDENTIFIER]


    def is_valid(self, identifier, lint_context):
        """ Whether all variables are used after declared.
        This policy cannot determine the following node types:
          - Global identifier like nodes
            - ENV
            - REG
            - OPTION
          - Dynamic variables
            - CURLYNAME
            - SLICE
            - DOT
            - SUBSCRIPT
        """

        if not is_reference_identifier(identifier):
            return True

        scope_plugin = lint_context['plugins']['scope']
        is_global = scope_plugin.is_global_variable(identifier)
        is_reachable = is_reachable_reference_identifier(identifier)

        # Ignore global like variables
        return is_reachable or is_global

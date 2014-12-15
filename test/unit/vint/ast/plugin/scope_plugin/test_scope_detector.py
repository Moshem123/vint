import pytest
from vint.ast.node_type import NodeType
from vint.ast.plugin.scope_plugin.scope_detector import ScopeDetector, ScopeVisibility as Vis
from vint.ast.plugin.scope_plugin.identifier_classifier import (
    IDENTIFIER_ATTRIBUTE,
    IDENTIFIER_ATTRIBUTE_DYNAMIC_FLAG,
    IDENTIFIER_ATTRIBUTE_DEFINITION_FLAG,
    IDENTIFIER_ATTRIBUTE_SUBSCRIPT_MEMBER_FLAG,
)


def create_scope(visibility):
    return {
        'scope_visibility': visibility,
    }


def create_scope_visibility_hint(visibility, is_implicit=False):
    return {
        'scope_visibility': visibility,
        'is_implicit': is_implicit,
    }


def create_id(id_value):
    return {
        'type': NodeType.IDENTIFIER.value,
        'value': id_value,
        IDENTIFIER_ATTRIBUTE: {
            IDENTIFIER_ATTRIBUTE_DEFINITION_FLAG: True,
            IDENTIFIER_ATTRIBUTE_DYNAMIC_FLAG: False,
            IDENTIFIER_ATTRIBUTE_SUBSCRIPT_MEMBER_FLAG: False,
        },
    }


def create_env(env_value):
    return {
        'type': NodeType.ENV.value,
        'value': env_value,
        IDENTIFIER_ATTRIBUTE: {
            IDENTIFIER_ATTRIBUTE_DEFINITION_FLAG: True,
            IDENTIFIER_ATTRIBUTE_DYNAMIC_FLAG: False,
            IDENTIFIER_ATTRIBUTE_SUBSCRIPT_MEMBER_FLAG: False,
        },
    }


def create_option(opt_value):
    return {
        'type': NodeType.OPTION.value,
        'value': opt_value,
        IDENTIFIER_ATTRIBUTE: {
            IDENTIFIER_ATTRIBUTE_DEFINITION_FLAG: True,
            IDENTIFIER_ATTRIBUTE_DYNAMIC_FLAG: False,
            IDENTIFIER_ATTRIBUTE_SUBSCRIPT_MEMBER_FLAG: False,
        },
    }


def create_reg(reg_value):
    return {
        'type': NodeType.REG.value,
        'value': reg_value,
        IDENTIFIER_ATTRIBUTE: {
            IDENTIFIER_ATTRIBUTE_DEFINITION_FLAG: True,
            IDENTIFIER_ATTRIBUTE_DYNAMIC_FLAG: False,
            IDENTIFIER_ATTRIBUTE_SUBSCRIPT_MEMBER_FLAG: False,
        },
    }


def create_curlyname():
    """ Create a node as a `my_{'var'}`
    """
    return {
        'type': NodeType.CURLYNAME.value,
        'value': [
            {
                'type': NodeType.CURLYNAMEPART.value,
                'value': 'my_',
            },
            {
                'type': NodeType.CURLYNAMEEXPR.value,
                'value': {
                    'type': NodeType.CURLYNAMEEXPR.value,
                    'value': 'var',
                },
            }
        ],
        IDENTIFIER_ATTRIBUTE: {
            IDENTIFIER_ATTRIBUTE_DEFINITION_FLAG: True,
            IDENTIFIER_ATTRIBUTE_DYNAMIC_FLAG: True,
            IDENTIFIER_ATTRIBUTE_SUBSCRIPT_MEMBER_FLAG: False,
        },
    }


def create_subscript_member():
    return {
        'type': NodeType.IDENTIFIER.value,
        'value': 'member',
        IDENTIFIER_ATTRIBUTE: {
            IDENTIFIER_ATTRIBUTE_DEFINITION_FLAG: True,
            IDENTIFIER_ATTRIBUTE_DYNAMIC_FLAG: False,
            IDENTIFIER_ATTRIBUTE_SUBSCRIPT_MEMBER_FLAG: True,
        },
    }


@pytest.mark.parametrize(
    'context_scope_visibility, id_node, expected_scope_visibility, expected_implicity', [
        (Vis.SCRIPT_LOCAL, create_id('g:explicit_global'), Vis.GLOBAL_LIKE, False),
        (Vis.SCRIPT_LOCAL, create_id('implicit_global'), Vis.GLOBAL_LIKE, True),
        (Vis.FUNCTION_LOCAL, create_id('g:explicit_global'), Vis.GLOBAL_LIKE, False),

        (Vis.SCRIPT_LOCAL, create_id('b:buffer_local'), Vis.GLOBAL_LIKE, False),
        (Vis.FUNCTION_LOCAL, create_id('b:buffer_local'), Vis.GLOBAL_LIKE, False),

        (Vis.SCRIPT_LOCAL, create_id('w:window_local'), Vis.GLOBAL_LIKE, False),
        (Vis.FUNCTION_LOCAL, create_id('w:window_local'), Vis.GLOBAL_LIKE, False),

        (Vis.SCRIPT_LOCAL, create_id('s:script_local'), Vis.SCRIPT_LOCAL, False),
        (Vis.FUNCTION_LOCAL, create_id('s:script_local'), Vis.SCRIPT_LOCAL, False),

        (Vis.FUNCTION_LOCAL, create_id('l:explicit_function_local'), Vis.FUNCTION_LOCAL, False),
        (Vis.FUNCTION_LOCAL, create_id('implicit_function_local'), Vis.FUNCTION_LOCAL, True),

        (Vis.FUNCTION_LOCAL, create_id('a:param'), Vis.FUNCTION_LOCAL, False),
        (Vis.FUNCTION_LOCAL, create_id('a:000'), Vis.FUNCTION_LOCAL, False),
        (Vis.FUNCTION_LOCAL, create_id('a:1'), Vis.FUNCTION_LOCAL, False),

        (Vis.SCRIPT_LOCAL, create_id('v:count'), Vis.BUILTIN, False),
        (Vis.FUNCTION_LOCAL, create_id('v:count'), Vis.BUILTIN, False),
        (Vis.FUNCTION_LOCAL, create_id('count'), Vis.BUILTIN, True),

        (Vis.SCRIPT_LOCAL, create_curlyname(), Vis.UNANALYZABLE, False),
        (Vis.FUNCTION_LOCAL, create_curlyname(), Vis.UNANALYZABLE, False),

        (Vis.SCRIPT_LOCAL, create_subscript_member(), Vis.UNANALYZABLE, False),
        (Vis.FUNCTION_LOCAL, create_subscript_member(), Vis.UNANALYZABLE, False),
    ]
)
def test_detect_scope_visibility(context_scope_visibility, id_node, expected_scope_visibility, expected_implicity):
    scope = create_scope(context_scope_visibility)
    scope_visibility_hint = ScopeDetector.detect_scope_visibility(id_node, scope)

    expected_scope_visibility_hint = create_scope_visibility_hint(expected_scope_visibility,
                                                                  is_implicit=expected_implicity)
    assert expected_scope_visibility_hint == scope_visibility_hint



@pytest.mark.parametrize(
    'context_scope_visibility, node, expected_variable_name', [
        (Vis.SCRIPT_LOCAL, create_id('g:explicit_global'), 'g:explicit_global'),
        (Vis.SCRIPT_LOCAL, create_id('implicit_global'), 'g:implicit_global'),

        (Vis.FUNCTION_LOCAL, create_id('l:explicit_function_local'), 'l:explicit_function_local'),
        (Vis.FUNCTION_LOCAL, create_id('implicit_function_local'), 'l:implicit_function_local'),

        (Vis.SCRIPT_LOCAL, create_id('v:count'), 'v:count'),
        (Vis.FUNCTION_LOCAL, create_id('v:count'), 'v:count'),
        (Vis.FUNCTION_LOCAL, create_id('count'), 'v:count'),

        (Vis.SCRIPT_LOCAL, create_env('$ENV'), '$ENV'),
        (Vis.SCRIPT_LOCAL, create_option('&OPT'), '&OPT'),
        (Vis.SCRIPT_LOCAL, create_reg('@"'), '@"'),
    ]
)
def test_normalize_variable_name(context_scope_visibility, node, expected_variable_name):
    scope = create_scope(context_scope_visibility)
    normalize_variable_name = ScopeDetector.normalize_variable_name(node, scope)

    assert expected_variable_name == normalize_variable_name



@pytest.mark.parametrize(
    'id_value, expected_result', [
        ('my_var', False),
        ('count', True),
        ('v:count', True),
    ]
)
def test_is_builtin_variable(id_value, expected_result):
    id_node = create_id(id_value)
    result = ScopeDetector.is_builtin_variable(id_node)

    assert expected_result == result

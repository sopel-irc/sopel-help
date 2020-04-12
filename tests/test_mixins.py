from sopel_help import mixins


def test_html_generator_generate_help_commands():
    mixin = mixins.HTMLGeneratorMixin()

    result = list(mixin.generate_help_commands({
        'group_a': ['command_a_a', 'command_a_b'],
        'group_c': ['command_c_a', 'command_c_b'],
        'group_b': ['command_b_a', 'command_b_b'],
    }))

    assert result == [
        '<h2>GROUP_A</h2><ul><li>command_a_a</li><li>command_a_b</li></ul>',
        '<h2>GROUP_B</h2><ul><li>command_b_a</li><li>command_b_b</li></ul>',
        '<h2>GROUP_C</h2><ul><li>command_c_a</li><li>command_c_b</li></ul>',
    ]

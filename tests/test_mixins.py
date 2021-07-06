from sopel_help import mixins


def test_html_generator_generate_help_commands():
    mixin = mixins.HTMLGeneratorMixin()

    result = list(mixin.generate_help_commands({
        'group_a': ['command_a_a', 'command_a_b'],
        'group_c': ['command_c_a', 'command_c_b'],
        'group_b': ['command_b_a', 'command_b_b'],
    }))

    assert result == [
        '<h2 id="plugin-group_a"><a href="#plugin-group_a">GROUP_A</a></h2>'
        '<ul><li>command_a_a</li><li>command_a_b</li></ul>',
        '<h2 id="plugin-group_b"><a href="#plugin-group_b">GROUP_B</a></h2>'
        '<ul><li>command_b_a</li><li>command_b_b</li></ul>',
        '<h2 id="plugin-group_c"><a href="#plugin-group_c">GROUP_C</a></h2>'
        '<ul><li>command_c_a</li><li>command_c_b</li></ul>',
    ]

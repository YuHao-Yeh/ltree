import argparse
import pytest

from list_tree.config import TreeConfig

@pytest.fixture
def base_args():
    return argparse.Namespace(
        output="-",
        ex_dirs=[],
        ex_files=[],
        ex_ext=[],
        ex_prefix=[],
        add_dirs=[],
        add_files=[],
        color=False,
        show_size=False,
        full_path=False,
        human_readable=False,
        show_all=False,
        folders_only=False,
        dirs_first=False,
        show_ellipsis=False
    )


#=======================================================================#
# Test: TreeConfig.apply_args()
#=======================================================================#
def test_config_apply_args_exclusions(base_args):
    config = TreeConfig()
    
    base_args.ex_dirs = ['my_node_modules', 'temp_dir']
    base_args.ex_files = ['config.secret', 'data.db']
    base_args.ex_ext = ['.log', '.tmp']
    base_args.ex_prefix = ['test_', 'tmp_']
    
    config.apply_args(base_args)
    
    assert 'my_node_modules' in config.exclude_dirs
    assert 'config.secret' in config.exclude_files
    assert '.log' in config.exclude_exts
    assert 'test_' in config.exclude_prefixes

def test_config_apply_args_reinclude(base_args):
    config = TreeConfig()
    
    assert '__pycache__' in config.exclude_dirs

    config.exclude_files.add('tree.txt')

    base_args.add_dirs = ['__pycache__']
    base_args.add_files = ['tree.txt']

    config.apply_args(base_args)
    
    
    assert '__pycache__' not in config.exclude_dirs
    assert 'tree.txt' not in config.exclude_files
    
    assert '__pycache__' in config.added_items
    assert 'tree.txt' in config.added_items

def test_config_color_logic(base_args):
    config = TreeConfig()
    
    # Case A: console output with color
    base_args.output = "-"
    base_args.color = True
    config.apply_args(base_args)
    assert config.use_color is True
    
    # Case B：file output with no color
    base_args.output = "out.txt"
    base_args.color = True
    config.apply_args(base_args)
    assert config.use_color is False

def test_config_pattern_preparation(base_args):
    config = TreeConfig()

    base_args.ex_files = ['*.log', 'debug_?_test.txt', 'fixed_name.txt']
    
    config.apply_args(base_args)

    assert '*.log' in config._pattern_files
    assert 'debug_?_test.txt' in config._pattern_files

    assert 'fixed_name.txt' in config._exact_files
    assert '*.log' not in config._exact_files

def test_config_flag_sync(base_args):
    config = TreeConfig()
    
    base_args.show_size = True
    base_args.folders_only = True
    base_args.full_path = True
    base_args.dirs_first = True
    
    config.apply_args(base_args)
    
    assert config.show_size is True
    assert config.folders_only is True
    assert config.full_path is True
    assert config.dirs_first is True

import argparse
import io
import pytest
import sys
from unittest.mock import MagicMock, patch, mock_open

from ltree.cli import parse_args, run, main


#=======================================================================#
# Fixture
#=======================================================================#
CLI_MODULE = "ltree.cli"
RENDERER_PATH = "ltree.renderers"

@pytest.fixture
def base_args():
    return argparse.Namespace(
        start_path='.',
        output='-',
        format='text',
        max_depth=None,
        color=True,
        show_size=False,
        human_readable=False,
        show_all=False,
        folders_only=False,
        no_ignore=True,
        regex_exclude=[],
        dirs_first=False,
        show_ellipsis=False,
        ex_dirs=[], ex_files=[], ex_ext=[], ex_prefix=[],
        add_dirs=[], add_files=[],
        full_path=False,
        theme='none'
    )

def create_mock_root(size=1024):
    root = MagicMock()
    root.size = size
    root.stats.visible_dirs = 1
    root.stats.visible_files = 1
    root.stats.total_dirs = 1
    root.stats.total_files = 1
    return root

#=======================================================================#
# Test: parse_arg
#=======================================================================#
def test_parse_args_defaults():
    with patch.object(sys, 'argv', ['list-tree']):
        args = parse_args()
        assert args.start_path == '.'
        assert args.output == '-'
        assert args.format == 'text'

def test_parse_args_custom():
    test_args = [
        'list-tree', 'my_path',
        '-o', 'out.txt',
        '-F', 'json',
        '-L', '2',
        '-f',
        '-a',
        '--dirs-first'
    ]
    with patch.object(sys, 'argv', test_args):
        args = parse_args()
        assert args.start_path == 'my_path'
        assert args.output == 'out.txt'
        assert args.format == 'json'
        assert args.max_depth == 2
        assert args.full_path is True
        assert args.show_all is True
        assert args.dirs_first is True

#=======================================================================#
# Test: run
#=======================================================================#
@patch(f'{CLI_MODULE}.scan_tree')
@patch(f'{RENDERER_PATH}.exporters.TextRenderer.render')
def test_run_file_output(mock_render_text, mock_scan, base_args):
    mock_scan.return_value = create_mock_root()
    base_args.output = 'test_output.txt'

    m = mock_open()
    with patch('builtins.open', m):
        run(base_args)
    
    m.assert_called_once_with('test_output.txt', 'w', encoding='utf-8')
    mock_render_text.assert_called_once()

@pytest.mark.parametrize("fmt, renderer_class", [
    ("text", "exporters.TextRenderer"),
    ("json", "exporters.JsonRenderer"),
    ("md", "exporters.MarkdownRenderer"),
    ("block", "exporters.MarkdownBlockRenderer"),
    ("rich", "rich_renderer.RichRenderer"),
])
@patch(f'{CLI_MODULE}.scan_tree')
@patch(f'{CLI_MODULE}.print_stats')
def test_run_formats_and_stats(mock_print_stats, mock_scan, fmt, renderer_class, base_args):
    mock_scan.return_value = create_mock_root()
    base_args.format = fmt
    base_args.output = "-"

    with patch(f'{RENDERER_PATH}.{renderer_class}.render') as mock_render:    
        with patch('sys.stdout', new_callable=io.StringIO):
            run(base_args)

        mock_render.assert_called_once()
        mock_scan.assert_called_once()
        if fmt != 'json':
            mock_print_stats.assert_called_once()

@patch(f'{CLI_MODULE}.scan_tree')
def test_run_no_exist_path(mock_scan, base_args):
    mock_scan.return_value = None
    
    assert run(base_args) is None

#=======================================================================#
# Test: main entry point
#=======================================================================#
def test_main_entry_point():
    with patch(f'{CLI_MODULE}.parse_args') as mock_parse:
        with patch(f'{CLI_MODULE}.run') as mock_run:
            mock_args = MagicMock()
            mock_parse.return_value = mock_args
            
            main()
            
            mock_parse.assert_called_once()
            mock_run.assert_called_once_with(mock_args)

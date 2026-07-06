# tests/test_cli/test_main.py
import sys
from unittest.mock import MagicMock, patch
from ltree.cli.main import main


cli_path = "ltree.cli.main"


def test_main_executes_func_on_subcommand():
    mock_func = MagicMock()
    mock_args = MagicMock()
    mock_args.func = mock_func

    with patch(f"{cli_path}.build_parser") as mock_build_parser, patch.object(
        sys, "argv", ["ltree"]
    ):
        mock_parser = MagicMock()
        mock_parser.parse_args.return_value = mock_args
        mock_build_parser.return_value = mock_parser

        main()

        mock_func.assert_called_once_with(mock_args)


def test_main_prints_help_when_no_subcommand_selected():
    with patch(f"{cli_path}.build_parser") as mock_build_parser, patch.object(
        sys, "argv", ["ltree"]
    ):
        mock_parser = MagicMock()
        mock_args = object()
        mock_parser.parse_args.return_value = mock_args
        mock_build_parser.return_value = mock_parser

        main()

        mock_parser.print_help.assert_called_once()

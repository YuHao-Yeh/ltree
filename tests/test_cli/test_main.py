# tests/test_cli/test_main.py
import sys
from unittest.mock import MagicMock, patch
from ltree.cli.main import main


cli_path = "ltree.cli.main"


def test_main_executes_func_on_subcommand():
    mock_func = MagicMock()
    mock_args = MagicMock()
    mock_args.func = mock_func

    with (
        patch(f"{cli_path}.build_parser") as mock_build_parser,
        patch.object(sys, "argv", ["ltree"]),
    ):
        mock_parser = MagicMock()
        mock_parser.parse_args.return_value = mock_args
        mock_build_parser.return_value = mock_parser

        main()

        mock_func.assert_called_once_with(mock_args)


def test_main_prints_help_when_no_subcommand_selected():
    with (
        patch(f"{cli_path}.build_parser") as mock_build_parser,
        patch.object(sys, "argv", ["ltree"]),
    ):
        mock_parser = MagicMock()
        mock_args = object()
        mock_parser.parse_args.return_value = mock_args
        mock_build_parser.return_value = mock_parser

        main()

        mock_parser.print_help.assert_called_once()


def test_main_sys_argv():
    # Case 1: empty argv
    test_argv = []

    with patch("sys.argv", test_argv):
        with patch("ltree.cli.main.build_parser") as mock_build_parser:
            mock_parser = MagicMock()
            mock_args = MagicMock()

            mock_parser.parse_args.return_value = mock_args
            mock_build_parser.return_value = mock_parser

            main()

            assert test_argv == ["ltree", "tree"]

    # Case 2: length of argv >= 2
    test_argv = ["ltree", "some/sandbox/dir"]

    with patch("sys.argv", test_argv):
        with patch("ltree.cli.main.build_parser") as mock_build_parser:
            mock_parser = MagicMock()
            mock_args = MagicMock()
            mock_parser.parse_args.return_value = mock_args
            mock_build_parser.return_value = mock_parser

            main()

            assert test_argv == ["ltree", "tree", "some/sandbox/dir"]

    # Case 3: no sys.argv attribute
    import sys

    with patch("ltree.cli.main.build_parser") as mock_build_parser:
        mock_parser = MagicMock()
        mock_args = MagicMock()
        mock_parser.parse_args.return_value = mock_args
        mock_build_parser.return_value = mock_parser

        has_argv = hasattr(sys, "argv")
        original_argv = sys.argv if has_argv else []
        if has_argv:
            del sys.argv

        try:
            main()
        finally:
            if has_argv:
                sys.argv = original_argv

        mock_build_parser.assert_called_once()


def test_main_permission_error_handling(capsys):
    mock_func = MagicMock()
    mock_func.side_effect = PermissionError("Access denied to target files")

    mock_args = MagicMock()
    mock_args.func = mock_func

    test_argv = ["ltree", "tree"]

    with patch("sys.argv", test_argv):
        with patch("ltree.cli.main.build_parser") as mock_build_parser:
            mock_parser = MagicMock()
            mock_parser.parse_args.return_value = mock_args
            mock_build_parser.return_value = mock_parser

            exit_code = main()

            assert exit_code == 1

            captured = capsys.readouterr()
            assert (
                "Error: Permission denied. Access denied to target files"
                in captured.err
            )


def test_main_generic_exception_handling(capsys):
    mock_func = MagicMock()
    mock_func.side_effect = ValueError("Some unexpected value error")

    mock_args = MagicMock()
    mock_args.func = mock_func

    test_argv = ["ltree", "tree"]

    with patch("sys.argv", test_argv):
        with patch("ltree.cli.main.build_parser") as mock_build_parser:
            mock_parser = MagicMock()
            mock_parser.parse_args.return_value = mock_args
            mock_build_parser.return_value = mock_parser

            exit_code = main()

            assert exit_code == 1

            captured = capsys.readouterr()
            assert (
                "Error: Unexpected failure. Some unexpected value error" in captured.err
            )

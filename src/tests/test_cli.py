from ficopilot import main


def test_main_prints_package_version(capsys) -> None:
    main()

    captured = capsys.readouterr()

    assert captured.out == "ficopilot 0.1.0\n"

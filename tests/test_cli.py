from ficopilot import main


def test_main_prints_welcome_message(capsys) -> None:
    main()

    captured = capsys.readouterr()

    assert captured.out == "Hello from ficopilot!\n"

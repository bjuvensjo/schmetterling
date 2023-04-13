from json import dumps
from re import match
from unittest.mock import call, mock_open, patch

from schmetterling.build.gradle import build
from schmetterling.build.gradle import create_command
from schmetterling.build.gradle import read_build_result


def test_build():
    with patch(
        "schmetterling.build.gradle.read_build_result",
        return_value={
            "/ZTEST/bar": {
                "group": "com.group",
                "name": "bar",
                "version": "1.0.0-SNAPSHOT",
                "build_status": "SUCCESS",
            },
            "/ZTEST/baz": {
                "group": "com.group",
                "name": "baz",
                "version": "1.0.0-SNAPSHOT",
                "build_status": "SUCCESS",
            },
            "/ZTEST/foo": {
                "group": "com.group",
                "name": "foo",
                "version": "1.0.0-SNAPSHOT",
                "build_status": "FAILURE",
                "message": "Execution failed for task ':foo:compileGroovy'.",
            },
        },
    ):
        with patch("schmetterling.build.gradle.create_command", return_value="command"):
            with patch(
                "schmetterling.build.gradle.run_command", return_value=(0, "success")
            ) as m:
                assert build("projects_dir") == {
                    "build_result": {
                        "/ZTEST/bar": {
                            "group": "com.group",
                            "name": "bar",
                            "version": "1.0.0-SNAPSHOT",
                            "build_status": "SUCCESS",
                        },
                        "/ZTEST/baz": {
                            "group": "com.group",
                            "name": "baz",
                            "version": "1.0.0-SNAPSHOT",
                            "build_status": "SUCCESS",
                        },
                        "/ZTEST/foo": {
                            "group": "com.group",
                            "name": "foo",
                            "version": "1.0.0-SNAPSHOT",
                            "build_status": "FAILURE",
                            "message": "Execution failed for task ':foo:compileGroovy'.",
                        },
                    },
                    "output": "success",
                }
                assert m.mock_calls == [
                    call(
                        "command",
                        check=False,
                        cwd="projects_dir",
                        return_output=True,
                        timeout=None,
                    ),
                ]


def test_create_command():
    assert match(
        r" ".join(
            [
                "gradle build -Dprojects_dir=projects_dir",
                "--project-cache-dir projects_dir",
                "--init-script .*/init.gradle --settings-file",
                ".*/settings.gradle --continue --configure-on-demand",
                "--parallel -q",
            ]
        ),
        create_command("projects_dir"),
    )


def test_read_build_result():
    with patch(
        "builtins.open",
        mock_open(
            read_data=dumps(
                {
                    "/ZTEST/bar": {
                        "group": "com.group",
                        "name": "bar",
                        "version": "1.0.0-SNAPSHOT",
                        "build_status": "SUCCESS",
                    },
                    "/ZTEST/baz": {
                        "group": "com.group",
                        "name": "baz",
                        "version": "1.0.0-SNAPSHOT",
                        "build_status": "SUCCESS",
                    },
                    "/ZTEST/foo": {
                        "group": "com.group",
                        "name": "foo",
                        "version": "1.0.0-SNAPSHOT",
                        "build_status": "FAILURE",
                        "message": "Execution failed for task ':foo:compileGroovy'.",
                    },
                }
            )
        ),
    ):
        assert read_build_result("build_dir") == {
            "/ZTEST/bar": {
                "group": "com.group",
                "name": "bar",
                "version": "1.0.0-SNAPSHOT",
                "build_status": "SUCCESS",
            },
            "/ZTEST/baz": {
                "group": "com.group",
                "name": "baz",
                "version": "1.0.0-SNAPSHOT",
                "build_status": "SUCCESS",
            },
            "/ZTEST/foo": {
                "group": "com.group",
                "name": "foo",
                "version": "1.0.0-SNAPSHOT",
                "build_status": "FAILURE",
                "message": "Execution failed for task ':foo:compileGroovy'.",
            },
        }


# TODO mock all side effects!!!
# def test_execute():
#     with patch('schmetterling.build.gradle.isinstance', return_value=True):
#         state = [
#             MagicMock(repos=[
#                 MagicMock(
#                     path=
#                     '/Users/magnus/slask/gradle/z/ZESIN/integration/getaccount/v1_0',
#                     build_status=Repo.STATUS_UPDATED),
#                 MagicMock(
#                     path=
#                     '/Users/magnus/slask/gradle/z/ZESIN/integration/gettransactions/v1_0',
#                     build_status=Repo.STATUS_UNCHANGED),
#             ])
#         ]
#         params = {}
#         build_status = execute(state, **params)
#         assert [Build.SUCCESS, Build.SUCCESS] == sorted(
#             [b.build_status for b in build_status.builds])

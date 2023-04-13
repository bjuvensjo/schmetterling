from unittest.mock import call, MagicMock, patch

from schmetterling.build.maven import build_multi_modules
from schmetterling.build.maven import create_build_result
from schmetterling.build.maven import create_command
from schmetterling.build.maven import create_multi_modules
from schmetterling.build.maven import create_state
from schmetterling.build.maven import get_maven_infos
from schmetterling.build.maven import get_maven_repos
from schmetterling.build.maven import get_multi_modules
from schmetterling.build.state import BuildState, Build
from schmetterling.setup.state import Repo


def test_build_multi_modules():
    mm = [
        {"updated": "updated1", "pom_dir": "pom_dir1", "coordinates": "coordinates1"},
        {"updated": "updated2", "pom_dir": "pom_dir2", "coordinates": "coordinates2"},
    ]
    with patch(
        "schmetterling.build.maven.create_command", return_value="create_command"
    ) as m_create_command, patch(
        "schmetterling.build.maven.run_command"
    ) as m_run_command, patch(
        "schmetterling.build.maven.create_build_result",
        return_value=[["success_coordinates"], ["failure_coordinates"]],
    ) as m_create_build_result:
        assert build_multi_modules(
            mm, "repository_dir", "settings_file", "logback_file"
        ) == (
            ["success_coordinates", "success_coordinates"],
            ["failure_coordinates", "failure_coordinates"],
        )
        assert m_create_command.mock_calls == [
            call(
                "updated1",
                "pom_dir1/mvn.log",
                "repository_dir",
                "settings_file",
                "logback_file",
            ),
            call(
                "updated2",
                "pom_dir2/mvn.log",
                "repository_dir",
                "settings_file",
                "logback_file",
            ),
        ]
        assert m_run_command.mock_calls == [
            call("create_command", cwd="pom_dir1"),
            call("create_command", cwd="pom_dir2"),
        ]
        assert m_create_build_result.mock_calls == [
            call("coordinates1", "updated1", "pom_dir1/mvn.log"),
            call("coordinates2", "updated2", "pom_dir2/mvn.log"),
        ]


def test_create_command():
    assert create_command(
        [
            {
                "artifact_id": "app.admin",
                "group_id": "mygroup",
            },
            {
                "artifact_id": "app.sign",
                "group_id": "mygroup",
            },
        ],
        "mvn.log",
        "repository",
        "settings.xml",
        "logback.xml",
    ) == str(
        "mvn -Dmaven.repo.local=repository "
        "-s settings.xml "
        "-DcreateChecksum=true "
        "-Dfile.encoding=UTF-8 "
        "-Dsun.jnu.encoding=UTF-8 "
        "-Dlogback.configurationFile=logback.xml "
        "-B -amd -pl mygroup:app.admin,mygroup:app.sign "
        "clean install javadoc:jar source:jar "
        "--fail-at-end | tee mvn.log"
    )


@patch(
    "schmetterling.build.maven.get_summary",
    return_value=(["mygroup:app.admin"], ["app.sign"]),
)
def test_create_build_result(mock_get_summary):
    assert create_build_result(
        [
            {
                "artifact_id": "app.admin",
                "group_id": "mygroup",
            },
            {
                "artifact_id": "app.sign",
                "group_id": "mygroup",
            },
            {
                "artifact_id": "pipeline.env",
                "group_id": "mygroup",
            },
            {
                "artifact_id": "xml.ws",
                "group_id": "mygroup",
            },
        ],
        [
            {
                "artifact_id": "app.admin",
                "group_id": "mygroup",
            },
            {
                "artifact_id": "app.sign",
                "group_id": "mygroup",
            },
            {
                "artifact_id": "pipeline.env",
                "group_id": "mygroup",
            },
        ],
        "mvn.log",
    ) == (
        [
            {
                "artifact_id": "app.admin",
                "group_id": "mygroup",
            },
        ],
        [
            {
                "artifact_id": "app.sign",
                "group_id": "mygroup",
            },
            {
                "artifact_id": "pipeline.env",
                "group_id": "mygroup",
            },
        ],
    )


def test_create_multi_modules():
    with patch("schmetterling.build.maven.makedirs") as m, patch(
        "schmetterling.build.maven.open"
    ) as o:
        f = MagicMock()
        o.return_value = MagicMock(__enter__=MagicMock(return_value=f))

        create_multi_modules(
            [
                {"pom_dir": "pd1", "pom_content": "pc1"},
                {"pom_dir": "pd2", "pom_content": "pc2"},
            ]
        )
        assert m.mock_calls == [call("pd1", exist_ok=True), call("pd2", exist_ok=True)]
        assert f.mock_calls == [call.write("pc1"), call.write("pc2")]


def test_create_state():
    state = BuildState(
        "schmetterling.build.maven",
        [
            Build(
                "mygroup", "app.admin", "0.0.1-SNAPSHOT", "app.admin", Build.SUCCESS, 1
            ),
            Build(
                "mygroup",
                "pipeline-apache-proxy",
                "1.0.0-SNAPSHOT",
                "pipeline-apache-proxy",
                Build.FAILURE,
                1,
            ),
        ],
    )
    assert (
        create_state(
            [],
            [
                {
                    "pom_path": "app.admin/pom.xml",
                    "artifact_id": "app.admin",
                    "group_id": "mygroup",
                    "version": "0.0.1-SNAPSHOT",
                    "packaging": "jar",
                }
            ],
            [
                {
                    "pom_path": "pipeline-apache-proxy/pom.xml",
                    "artifact_id": "pipeline-apache-proxy",
                    "group_id": "mygroup",
                    "version": "1.0.0-SNAPSHOT",
                    "packaging": "jar",
                }
            ],
            1,
        )
        == state
    )


def test_get_maven_info():
    with patch("schmetterling.build.maven.get_pom_info", side_effect=lambda x: x):
        repos = [
            MagicMock(status=Repo.STATUS_UPDATED, path="path1"),
            MagicMock(status=Repo.STATUS_UNCHANGED, path="path2"),
        ]
        assert get_maven_infos(repos) == [
            (True, "path1/pom.xml"),
            (False, "path2/pom.xml"),
        ]


def test_get_maven_repos():
    with patch("schmetterling.build.maven.isinstance", return_value=True):
        with patch("schmetterling.build.maven.exists", side_effect=[False, True]):
            m = MagicMock(path="pom_repo", return_value="pom_repo")
            state = [
                MagicMock(
                    repos=[
                        MagicMock(path="non_pom_repo"),
                        m,
                    ]
                )
            ]
            assert get_maven_repos(state) == [m]


def test_get_multi_modules():
    with patch("schmetterling.build.maven.get_pom", return_value="pom_content"):
        assert get_multi_modules([(False, {})], "build_dir") == []
        assert get_multi_modules([(True, {})], "build_dir") == [
            {
                "coordinates": [{}],
                "pom_content": "pom_content",
                "pom_dir": "build_dir/jar-modules",
                "updated": [{}],
            }
        ]
        assert get_multi_modules([(True, {"packaging": "jar"})], "build_dir") == [
            {
                "coordinates": [{"packaging": "jar"}],
                "pom_content": "pom_content",
                "pom_dir": "build_dir/jar-modules",
                "updated": [{"packaging": "jar"}],
            }
        ]
        assert get_multi_modules(
            [(True, {"artifact_id": "super-pom", "packaging": "pom"})], "build_dir"
        ) == [
            {
                "coordinates": [{"artifact_id": "super-pom", "packaging": "pom"}],
                "pom_content": "pom_content",
                "pom_dir": "build_dir/super-pom-modules",
                "updated": [{"artifact_id": "super-pom", "packaging": "pom"}],
            }
        ]
        assert get_multi_modules(
            [(True, {"artifact_id": "pom", "packaging": "pom"})], "build_dir"
        ) == [
            {
                "coordinates": [{"artifact_id": "pom", "packaging": "pom"}],
                "pom_content": "pom_content",
                "pom_dir": "build_dir/pom-pom-modules",
                "updated": [{"artifact_id": "pom", "packaging": "pom"}],
            }
        ]
        assert get_multi_modules(
            [(True, {"artifact_id": "x", "packaging": "x"})], "build_dir"
        ) == [
            {
                "coordinates": [{"artifact_id": "x", "packaging": "x"}],
                "pom_content": "pom_content",
                "pom_dir": "build_dir/other-modules",
                "updated": [{"artifact_id": "x", "packaging": "x"}],
            }
        ]
        assert get_multi_modules(
            [(True, {"artifact_id": "war", "packaging": "war"})], "build_dir"
        ) == [
            {
                "coordinates": [{"artifact_id": "war", "packaging": "war"}],
                "pom_content": "pom_content",
                "pom_dir": "build_dir/war-modules",
                "updated": [{"artifact_id": "war", "packaging": "war"}],
            }
        ]
        assert get_multi_modules(
            [
                (True, {"artifact_id": "jar1", "packaging": "jar"}),
                (True, {"artifact_id": "jar2"}),
                (False, {"artifact_id": "jar3"}),
                (True, {"artifact_id": "war", "packaging": "war"}),
            ],
            "build_dir",
        ) == [
            {
                "coordinates": [
                    {"artifact_id": "jar1", "packaging": "jar"},
                    {"artifact_id": "jar2"},
                    {"artifact_id": "jar3"},
                ],
                "pom_content": "pom_content",
                "pom_dir": "build_dir/jar-modules",
                "updated": [
                    {"artifact_id": "jar1", "packaging": "jar"},
                    {"artifact_id": "jar2"},
                ],
            },
            {
                "coordinates": [{"artifact_id": "war", "packaging": "war"}],
                "pom_content": "pom_content",
                "pom_dir": "build_dir/war-modules",
                "updated": [{"artifact_id": "war", "packaging": "war"}],
            },
        ]

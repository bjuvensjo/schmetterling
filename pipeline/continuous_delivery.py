#!/usr/bin/env python3

from os import environ
from time import sleep

from schedule import every, run_all, run_pending
from vang.core.core import create_timestamp

from schmetterling.pipeline import pipeline

delivery_dir = "/Users/magnus/slask/schmetterling"
timestamp = create_timestamp()
log_dir = f"{delivery_dir}/logs/{timestamp}"

steps = [
    {
        "module": "schmetterling.log.log",
        "params": {"log_dir": log_dir, "name": "schmetterling", "level": "DEBUG"},
    },
    {"module": "schmetterling.state.load", "params": {"root": delivery_dir}},
    {
        "module": "schmetterling.setup.bitbucket",
        "params": {
            "url": "http://cuso.edb.se/stash",
            "username": environ["U"],
            "password": environ["P"],
            "setup_dir": f"{delivery_dir}/setup",
            "setup_branch": "develop",
            "projects": {"ZTEST": {"excludes": ["ws", "s1"], "includes": []}},
        },
    },
    {"module": "schmetterling.tag.git_delivery", "params": {"timestamp": timestamp}},
    {
        "module": "test.foo",
        "params": {"param1": "param1_value", "param2": "param2_value"},
    },
    {
        "module": "schmetterling.build.maven",
        "params": {
            "build_dir": f"{delivery_dir}/build/develop",
            "repository_dir": f"{delivery_dir}/repository/develop",
            "settings_file":
            # f'{delivery_dir}/setup/develop/PCS1806/maven.settings/src/main/resources/settings.xml',
            "/Users/magnus/.m2/settings.xml",
            "logback_file": "/Users/magnus/git/schmetterling/config/logback.xml",
            "timestamp": timestamp,
        },
    },
    {
        "module": "schmetterling.build.gradle",
        "params": {"projects_dir": f"{delivery_dir}/setup", "timestamp": timestamp},
    },
    #     {
    #     'module': 'schmetterling.analyze.sonarqube',
    #     'params': {
    #         'log_dir': log_dir,
    #         'settings_file':
    #             f'{delivery_dir}/setup/develop/XXXL/maven.settings/src/main/resources/settings.xml',
    #         'sonar_plugin': 'org.sonarsource.scanner.maven:sonar-maven-plugin:3.5.0.1254',
    #         'sonar_url': 'http://ext.local:9001',
    #         'sonar_auth_token': 'dbef1abdbb6f61faa9d7012a472d0375b6e8dde1'
    #     }
    # },
    {"module": "schmetterling.push.git"},
    #     {
    #     'module': 'schmetterling.hook.bitbucket',
    #     'params': {
    #         'hook': f'http://{environ["HOST_IP"]}:{environ["HOST_PORT"]}/schmetterling/webhook/'
    #     }
    # },
    {"module": "test.bar"},
    {
        "execute": lambda state, **params: print(
            "#" * 80, "##### lambda", "#" * 80, sep="\n"
        )
    },
    #     {
    #     'module': 'schmetterling.build_status.bitbucket',
    #     'params': {
    #         'url': 'http://cuso.edb.se/stash',
    #         'build_log_params': {
    #             'protocol': 'http',
    #             'host': environ['HOST_IP'],
    #             'port': environ['HOST_PORT'],
    #             'root': delivery_dir
    #         }
    #     }
    # },
    {
        "module": "schmetterling.state.dump",
        "params": {"root": delivery_dir, "timestamp": timestamp},
    },
]


def schedule():
    every(20).seconds.do(pipeline, steps)
    # every().hour.do(job)
    # every().day.at("10:30").do(job)
    # every(5).to(10).minutes.do(job)
    # every().monday.do(job)
    # every().wednesday.at("13:15").do(job)

    run_all()
    while True:
        run_pending()
        sleep(1)


if __name__ == "__main__":
    # schedule()
    pipeline(steps)

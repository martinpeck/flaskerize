import pytest
import os

from flaskerize.exceptions import InvalidSchema
from flaskerize.parser import FzArgumentParser, Flaskerize


def test_flaskerize_generate():

    status = os.system("fz generate --dry-run app my/test/app")
    assert status == 0
    assert not os.path.isfile("should_not_create.py")


def test__load_schema(tmp_path):
    from flaskerize.parser import _load_schema

    CONTENTS = """{"wrong_key":[]}"""
    schematic_dir = os.path.join(tmp_path, "schematics/test_schema")
    schema_filename = os.path.join(schematic_dir, "schema.json")
    os.makedirs(schematic_dir)
    with open(schema_filename, "w") as fid:
        fid.write(CONTENTS)
    with pytest.raises(InvalidSchema):
        cfg = _load_schema(schema_filename)


def test_schema(tmp_path):
    from flaskerize.parser import FzArgumentParser

    CONTENTS = """{"options":[]}"""
    schematic_dir = os.path.join(tmp_path, "schematics/test_schema")
    schema_filename = os.path.join(schematic_dir, "schema.json")
    schema_filename2 = os.path.join(schematic_dir, "schema2.json")
    os.makedirs(schematic_dir)
    with open(schema_filename, "w") as fid:
        fid.write(CONTENTS)
    with open(schema_filename2, "w") as fid:
        fid.write(CONTENTS)
    parser = FzArgumentParser(
        schema=schema_filename, xtra_schema_files=[schema_filename2]
    )
    assert parser


def test_bundle(tmp_path):
    import os

    CONTENTS = """import os
    from flask import Flask

    def create_app():
        app = Flask(__name__)

        @app.route("/health")
        def serve():
            return "{{ name }} online!"

        return app

    if __name__ == "__main__":
        app = create_app()
        app.run()"""

    app_file = f"{tmp_path}/app.py"
    with open(app_file, "w") as fid:
        fid.write(CONTENTS)

    INDEX_CONTENTS = """<!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <link rel="shortcut icon" href="/favicon.ico" />
        <meta name="viewport" content="width=device-width,initial-scale=1" />
        <title>Test</title>
      </head>
      <body>
    
      </body>
    </html>"""
    site_dir = f"{tmp_path}"
    with open(os.path.join(site_dir, "index.html"), "w") as fid:
        fid.write(INDEX_CONTENTS)

    status = os.system(f"fz bundle --dry-run -from {site_dir} -to app:create_app")

    assert status == 0


def test__check_validate_package(tmp_path):
    tmp_app_path = os.path.join(tmp_path, "test.py")
    fz = Flaskerize(["fz", "generate", "app", tmp_app_path])

    with pytest.raises(ModuleNotFoundError):
        fz._check_validate_package(os.path.join(tmp_path, "pkg that does not exist"))


def test__check_get_schematic_dirname(tmp_path):
    tmp_pkg_path = os.path.join(tmp_path, "some/pkg")
    os.makedirs(tmp_pkg_path)
    fz = Flaskerize(["fz", "generate", "app", tmp_pkg_path])

    with pytest.raises(ValueError):
        fz._check_get_schematic_dirname(
            tmp_pkg_path
            # os.path.join(tmp_path, "pkg that does not exist")
        )


def test__check_get_schematic_path(tmp_path):
    tmp_schematic_path = os.path.join(tmp_path, "some/pkg")
    os.makedirs(tmp_schematic_path)
    fz = Flaskerize(["fz", "generate", "app", tmp_schematic_path])

    with pytest.raises(ValueError):
        fz._check_get_schematic_path(
            tmp_schematic_path, "schematic that does not exist"
        )


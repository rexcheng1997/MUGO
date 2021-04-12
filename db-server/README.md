# Database Server
Two docker containers are required to run together in order to start the database server: `db-server` and `mysql-db`.

You have two options to start the database server:
- Run the `mysql-db` in a docker container, and run the `db-server` locally. *This option is for development purpose.*

    1. Start the `mysql-db` docker container with
    ```bash
    ./start.sh
    ```

    2. Run `db-server` locally with
    ```bash
    export FLASK_APP=server.py
    flask run
    ```
- Run both in a docker container group. *This option is for production purpose.*

    1. Change the current workding directory to the root of the project. If you are already under `db-server` folder, navigate to its parent folder.

    2. Run
    ```bash
    docker-compose up
    ```

    3. The docker container group will be available at `localhost:5001`.

## Error Message Format
There are two kinds of errors that can happen on the database server:
- `Validation error`: Request input misses required field in the database table.

    This kind of errors will be caught by `marshmallow`. See code example for how to write code to handle this kind of errors.

- `Database error`: Request input violates database table constraints.

    This kind of errors requires manual `try except` block wrapping around the database operations.

To keep error messages consistent and easier for the front end to handle, the above two kinds of errors should be returned in the following format:
```json
{
    "<column name 1>": [
        "<error message 1>",
        "<error message 2>",
        ...
    ],
    "<column name 2>": [
        ...
    ],
    ...
}
```
where `<column name>` needs to be replaced with the name of the table column that causes the error and `<error message>` needs to be replaced with the actual error message.

# Trade tariff reference

The trade tariff reference application is a django application that runs along side [trade-tariff-management](https://github.com/uktrade/trade-tariff-management).
The application generates and updates Free Trade Agreement and Most Favoured Nation (FTA and MFN) documents based on the trade tariff data and manages any subsequent changes to this data.


1.  Clone the repository:

    ```shell
    git clone https://github.com/uktrade/trade-tariff-reference
    cd trade-tariff-reference
    ```

2.  Create a `.env` file from `sample.env`

    ```shell
    cp sample.env .env
    ```
    Read the trade-tariff-reference playbook and update any blank keys accordingly.


3.  Build and run the necessary containers for the required environment:

    ```shell
    docker-compose build
    ```
4.  Import the database:

    The application requires a copy of the trade tariff data set to be able to generate the reference documents.
    To set the application up there are two options; a direct import of the data into the reference application or by running [trade-tariff-management](https://github.com/uktrade/trade-tariff-management) locally.
    - Obtain a copy of the tariff data set.
    - Either follow the trade-tariff-management installation instructions and skip the rest of this step or
    - Place the sql dump file in `trade-tariff-reference/sql` directory.
    - Rename the sql file to `tariff_uk.dump`
    - Update `.env` file set `UK_TARIFF_HOST=trade_application_db` and `UK_TARIFF_DB=tariff_uk`

    ```shell
    docker-compose run trade_application  bash ./scripts/import_db.sh
    ```

5.  Run the services:

    ```shell
    docker-compose up
    ```
    
6.  Run setup from within the container

    This will prompt to create a super user (add the email address of your user and enter any random string for a password as this will not be used), it will also add all additional data that is not found in the trade tariff database and it will generate all documents.
    N.B it will take a few minutes to generate all the documents.

    ```shell
    docker exec -ti tariff_trade_application_1  bash ./scripts/setup.sh
    ```

7.  Visit website

    ```shell
    http://localhost:8000/
    ```

If `DEVELOPMENT_SERVER` is set to true in the `.env` file then webserver will not be running automatically.
To run the webserver follow these extra steps before visiting the web site.

8.  Enter container

    ```shell
    docker exec -ti tariff_trade_application_1 /bin/bash
    ```

9.  Run application from within the container

    ```shell
    ./run.sh
    ```

To run tests

```shell
./run_tests.sh
```

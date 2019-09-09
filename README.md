# Trade tariff reference

1.  Clone the repository:

    ```shell
    git clone https://github.com/uktrade/trade-tariff-reference
    cd trade-tariff-reference
    ```

2.  Create a `.env` file from `sample.env`

    ```shell
    cp sample.env .env

3.  Build and run the necessary containers for the required environment:

    ```shell
    docker-compose build
    ```
4.  Import the databases (optional):

    ```shell
    docker-compose run trade_application  bash ./import_db.sh
    ```
5.  Run the services:

    ```shell
    docker-compose up
    ```
    
6.  Run setup from within the container

    ```shell
    docker exec -ti tariff_trade_application_1  bash ./setup.sh
    ```

7.  Visit website

    ```shell
    http://localhost:8000/
    ```

If `DEVELOPMENT_SERVER` is set to true then webserver will not be running automatically.
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

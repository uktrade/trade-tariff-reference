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
    docker-compose run tariffs ./import_db.sh
    ```
5.  Run the services:

    ```shell
    docker-compose up
    ```
    
6.  Enter container

    ```shell
    docker exec -ti trade-tariff-reference_tariffs_1 /bin/bash
    ```
    
7.  Run setup from within the container

    ```shell
    ./setup.sh
    ```

8.  Run application from within the container

    ```shell
    ./run.sh
    ```
    
9.  Visit website

    ```shell
    http://localhost:8000/
    ```


To run tests

```shell
./run_tests.sh
```

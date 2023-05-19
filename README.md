## Two Factors Authentication Python Backend

This is a simple python backend for two factors authentication.
The application allows the user to register and login using a username and password.
The user could also specify if he wants to use two factors authentication during the registration process.

The application is based on the FastAPI framework.
The current implementation uses a simple Postgres database to store the user information.

### Behaviour

#### Registration
The registration process is the following:

1. The user sends a POST request to the `/register` endpoint with email, password, basic profile info and 2FA flag in the body.
2. The server checks if the email is already used.
3. If the email is not used, the server creates a new user in the database storing the password encrypted using bcrypt.

#### Authentication without 2FA
In case the user decides to not rely on 2FA, the authentication process is the following:

1. The user sends a POST request to the `/login` endpoint with the username and password in the body.
2. The server checks if the username and password are correct.
3. If the username and password are correct, the server returns a JWT token to the user.
4. The user can use the JWT token to access the protected endpoints.

#### Authentication with 2FA
In case the user decides to rely on 2FA, the authentication process is the following:

1. The user sends a POST request to the `/login` endpoint with the username and password in the body.
2. The server checks if the username and password are correct.
3. If the username and password are correct, the server returns a temporary JWT token to the user with a generated OTP hashed using bcrypt.
4. The server will also send an email to the user with the OTP (in clear text).
5. The user call a new endpoint `/login/otp` with the OTP in the body and the temporary JWT token in the header.
6. The server compares the OTP sent by the user with the OTP stored in the temporary JWT token.
7. If the OTPs are the same, the server returns a new JWT token to the user.
8. The user can use the JWT token to access the protected endpoints.

#### OTP Generation
The OTP is generated using a super simple random algorithm, in the current version I decided to not use a more complex algorithm like TOTP or HOTP
because the expiration and security is delegated to the JWT token. In fact, the OTP is stored in the JWT token and hashed using bcrypt, the hashing should be enought to guarantee the obfuscation of the OTP.
In case an attacker could find a way to sign the JWT token, he could actually directly generate the final JWT avoiding all the OTP generation process.

#### Endpoints Documentation
The endpoints OpenAPI documentation is available at the `/docs` endpoint and also in the openapi.json file.

## Development

#### Setup local development environment
The Makefile contains all the commands to setup the local development environment.

Before running the commands, I suggest to setup a local virtual environment using `venv` or `conda`.

To setup the local development environment run the following command:
```bash
make setup-local-env
```
It will install pip-tools and all development requirements.
It also will setup `pre-commit` hooks to run linting and formatting before each commit.
The project also relies on `commitizen` to enforce the commit message format and handle tags.

#### Install application dependencies

To install the application dependencies run the following command:
```bash
make install
```

If new requirements are needed it is possible to add then on the `requirements.in` file and then run the following command:
```bash
make requirements.txt
```
It will generate the `requirements.txt` file with all the dependencies pinned using `pip-compile`.

#### Run the application on local environment

To run the application on local environment run the following command:
```bash
make run-local
```
It will read environment variables from the `.env.local` file.

#### Run the application on docker

To run the application on docker run the following command:
```bash
make run-docker
```
It will read environment variables from the `.env.docker` file and after building the docker image it will run the application on port 5050.

#### Run the application on docker-compose

To run the application on docker-compose run the following command:
```bash
docker compose up
```

#### Run the tests
Tests are written using pytest and contained in the `tests` folder.

To run the tests run the following command:
```bash
make test
```

It also possible to run the tests inside a docker container using the following command:
```bash
make test-docker
```

#### Database DDL

The database DDL is contained in the `db_schema` folder.

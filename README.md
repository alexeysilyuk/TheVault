# TheVault
#### Synopsis
Simulates working of vault.<br />
Receives form-data from user by api or via root routing html file.<br />
Encrypts it and stores in volatile(Redis) or permanent(file) storage, after succes storing user will receive encryption key.
After encryption user may send this key to api and in case of presense in storage, data will be decoded and returned to user.

#### Prerequisites
* docker
#### Install steps
1. Clone the code
1. docker-compose build
1. docker-compose up
1. go to http://localhost:8080 or http://localhost:8080/docs

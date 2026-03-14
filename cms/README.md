# README #

### Run project ###

```sh
cd new_website
cp new_website/settings_local.base new_website/settings_local.py
```

Install docker, docker-compose
For ubuntu - https://docs.docker.com/install/linux/docker-ce/ubuntu/
Postinstall for ubuntu - https://docs.docker.com/install/linux/linux-postinstall/
Install docker-compose - https://docs.docker.com/compose/install/#install-compose

Build docker containers
```sh
docker-compose build
```

Run project (http://127.0.0.1:8001)
```sh
docker-compose up -d
```

Project use DB from python-app project. This DB is read only. 
You should dump data from Staging server or Production server.
For help, you can contact DevOps or BackEnd developers.

Stop project
```sh
docker-compose down
```

Build docker containers without cache
```sh
docker-compose build --no-cache
```

Git branches

- **master** is the branch for Production
- **develop** is the branch for Staging
- **qa** is the branch for QA Server

You should start new **feature** branch from **develop** branch. 
Create pull request **feature** branch into **qa**. 
After testing on QA server you should create pull reqeust **feature** into **develop** and **develop** into **master**.

branch you should start from **master** branch and create a pull 
reqeust **hotfix** branch into **master**, **develop**, **qa**.


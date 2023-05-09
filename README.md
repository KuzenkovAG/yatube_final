# Yatube v.0.4.0 Final
Social network. 

## Features
- View Posts;
- Signup and login; 
- View detail of post;
- Create or Update own posts.

### New features
- Add follows;
- Add comments to posts.

## History of Yatube project
- v.0.4.0 [Final]  <- You are here
- v.0.3.0 [UnitTest] - Create tests.
- v.0.2.0 [Forms] - Add ability to create new posts. Add auth of User.
- v.0.1.0 [Community] - Ability to view posts.

## Tech
- Python 3.9
- Django 2.2

#### Tested Python version
Python 3.7-3.9


## Installation (for Windows)
Clone repository
```sh
git clone git@github.com:KuzenkovAG/yatube_final.git
```
Install environment
```sh
python -m venv venv
```
Activate environment
```sh
source venv/Scripts/activate
```
Install requirements
```sh
pip install -r requirements.txt
```
Make migrate
```sh
python yatube/manage.py migrate
```
Run server
```sh
python yatube/manage.py runserver
```

## Usage
Index page
```sh
http://127.0.0.1:8000/
```
Page of post
```sh
http://127.0.0.1:8000/posts/1/
```
Create post
```sh
http://127.0.0.1:8000/create/
```
Page of User
```sh
http://127.0.0.1:8000/profile/user_name/
```
Page of group
```sh
http://127.0.0.1:8000/group/group_slug/
```
Page of follows
```sh
http://127.0.0.1:8000/follow/
```


## Author
[Alexey Kuzenkov]


   [Alexey Kuzenkov]: <https://github.com/KuzenkovAG>

   [Final]: <https://github.com/KuzenkovAG/yatube_final>
   [UnitTest]: <https://github.com/KuzenkovAG/yatube_tests>
   [Forms]: <https://github.com/KuzenkovAG/yatube_forms>
   [Community]: <https://github.com/KuzenkovAG/yatube_community>
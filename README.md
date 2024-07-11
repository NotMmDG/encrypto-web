Hello this project deploys a simple website using docker.
project uses mysql for database and has access to phpmyadmin to control the database.
the project main goal is to build a website in  which you can create a user then upload files which the website will encrypt them and give you a password
by which you can download the files you uploaded in the website.
project is not optimized to hold heavy files like videos or ...
feel free to check out the example inside http://188.245.83.174:443/dashboard


how to use:
clone the project on your server or computer by
```sh
git clone https://github.com/NotMmDG/encrypto-web.git
```
then enter the project directory
```sh
cd encrypto-web
```
after you're in the main directory of the project you can change the variables from .env file 
```sh
nano .env
```
after you're done you can run the project by
```sh
sudo bash install.sh
```
after the project runs you can access it in:
http://localhost:443/dashboard
also phpmyadmin is available in http://localhost:8080
if you're running the project on a server use your server's ip instead of localhost
enjoy!

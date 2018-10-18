# Autodesk Froge API + Django Sample

Sample code of simple python library for Forge API, Django project includes the library, and javascript Forge Viewer Extensions.<br>
This is just for my self-training and investigation.  


---
## Features
* Python simple library for :
    * [Forge OAth2 APIs](https://forge.autodesk.com/en/docs/oauth/v2/developers_guide/overview/)
    * [Forge Data Managenet APis](https://forge.autodesk.com/en/docs/data/v2/developers_guide/overview/)
    * [Forge Model Delivertive APIs](https://forge.autodesk.com/en/docs/model-derivative/v2/developers_guide/overview/)
    * [memo] these libraries don't fully APIs support, but just several basic APIs only.
* Implementation of Forge 3-legged Authentication log-in on Django 1.10. 
* Implementation of Forge Access token contorol related with Django session dictionary.
* Increase jsree ajax performance by DB cache of hub folder hierarchy.
* Forge Viewer Extension Samples, collaborated with "jstree", "datatable.net", "ECharts".
* [Gentelella on Django](https://github.com/GiriB/django-gentelella) template base responsive design. 

 
---
## Requirements

#### Python 
* python 2.7.15  
* And see `requirement.txt`
        
```
beautifulsoup4==4.6.0  
bleach==3.0.2      
certifi==2018.8.24  
chardet==3.0.4  
Django==1.10  
django-cors-headers==2.4.0  
django-markdownify==0.8.0  
django-modelcluster==3.1  
django-taggit==0.22.2  
django-treebeard==4.3  
djangorestframework==3.6.4  
html5lib==0.999999999  
idna==2.7  
Markdown==3.0.1  
Pillow==5.3.0  
pytz==2018.5  
requests==2.19.1  
six==1.11.0  
Unidecode==1.0.22  
urllib3==1.23  
webencodings==0.5.1   
Willow==0.4
```  

#### Javascript
* Autodesk Forge viewer3D
* Bootstrap
* dataTables.net
* ECharts
* Font Awesome
* jQuery
* jquery.cookie
* jquery.storageapi
* jqvmap
* jstree
* moment


#### Browser Support
cf. [Forge Viewer Overview](https://forge.autodesk.com/en/docs/viewer/v6/developers_guide/overview/)
> The Viewer requires a WebGL-canvas compatible browser:
>
> * Chrome 50+
> * Firefox 45+
> * Opera 37+
> * Safari 9+
> * Microsoft Edge 20+
> * Internet Explorer 11


---
## Steps

#### Preparation    
* Create your Autodesk account and resist your App. See: [Tutorial : Create an App](https://forge.autodesk.com/en/docs/oauth/v2/tutorials/create-app/)
* Following the tutorial, prepare your App `client id` and `secrect key`.
* Get access to BIM360 Docs / Team site, and publish RVT files what ever you like.
* Install Python 2.7.15 and pip on your desktop. 

#### Get the Code

```text
$ git pull https://github.com/yusuk-mori/forge-django-sample.git
```

#### Install Requirements
```text
$ pip install -r requirement.txt
```

#### Update Configuration
Copy configuration sample file
```text
$ cp ./forge_django/environment.json.sample ./forge_django/environment.json
```
And update like the following :

```json
{
  "host_map": {
    "YOUR_PRODUCTION_HOSTNAME": "Production",
    "YOUR_STAGE_HOSTNAME": "Stage",
    "YOUR_DEV_HOSTNAME": "Development",
    "YOUR_LOCAL_HOSTNAME": "Development" //replace 'YOUR_LOCAL_HOSTNAME' to your actual host name.
  },
  "type_definition": {
    "Development":{
        //Update your settings for development.
        "FORGE_CLIENT_ID": "Your App Clinet ID",
        "FORGE_CLIENT_SECRET": "Your App Secret Key",
        "FORGE_AUTH_CALLBACK" : "Your APP 3-Legged Authentication Callback URL",
        "ALLOWED_HOSTS": ["localhost", "127.0.0.1"]
    }
  }
}
```

[MEMO]  
  
This application determine environment mode (ex.Development) based on executed host name.  
You should update this configuration file appropriately, 
and you can check it by `python -c "import socket; print socket.gethostname()"`.  
Without this,`python manage.py runserver` command is failed. 
  

#### Django initialization
```text
$ python manage.py makemigrations
$ python manage.py migrate
$ python manage.py createsuperuser
```

#### lanch Application Server
```text
$ python manage.py runserver

Performing system checks...

System check identified no issues (0 silenced).
October 18, 2018 - 12:13:55
Django version 1.10, using settings 'forge_django.settings.dev'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```
And access `http://localhost:8000`

---
## Demo Site
TBD

---
## Captures
* Dynamic property table sample includes datatable.net  
<img src="static/images/screenshot1.png" alt="screenshot1" width="400">
  
* Dynamic statistic charts sample includes Echarts  
<img src="static/images/screenshot2.png" alt="screenshot2" width="400"> 
  
* Responsive Design based on Bootstrap 3  
<img src="static/images/screenshot3.png" alt="screenshot3" width="200">


---
## Special Thanks
A lots of javascript features referenced  :   

* [Gentelella](https://github.com/puikinsh/gentelella)
* [Gentelella on Django](https://github.com/GiriB/django-gentelella)
* [Colorlib](https://colorlib.com/wp/free-bootstrap-admin-dashboard-templates/)
 
---
## License information
Copyright (c) Autodesk, Inc. All rights reserved   
Written by Yusuke Mori, Autodesk Consulting 2018   
  
This software is provided as is, without any warranty that it will work. You choose to use this tool at your own risk.  
Neither Autodesk nor the authors can be taken as responsible for any damage this tool can cause to your data.  
Please always make a back up of your data prior to use this tool.  

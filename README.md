
## Fred Hutch VIVO

The project is broken up into two main components:

 * `app` - the VIVO web application. VIVO related changes - theme, template changes, added controllers, etc. 
 * `toolkit` - the Converis to VIVO data syncing code

### Application overview

Built with VIVO 1.9.1

* The project uses the [custom installer](https://wiki.duraspace.org/display/VIVODOC19x/Installing+VIVO) pattern documented by the VIVO project. 
* The `webapp/src/main/webapp/themes` directory contains the CSS and template changes for this project. 

#### Installing FredHutch VIVO
* Clone the FredHutch VIVO
 * `git clone https://github.com/blevinefhcrc/fhutch-vivo.git`
* Change to the app directory
 * `cd app`
* Copy `sample-installer.xml` to `settings.xml` and adjust the settings to match your database, tomcat directory, VIVO home directory.
 * `cp sample-insstaller.xml settings.xml`
* Install the customized VIVO installation
 * `mvn install -s settings.xml`


### Toolkit overview

The Converis to VIVO toolkit is written in Python and utilizes the Converis web services.

 * Each of the .py scripts in the tookit directory reflect a group of data in Converis - e.g. `people.py`, `publications.py`, etc.
 * `models.py` contains the logic to map a Converis entity to a VIVO entity
 * `rebuild.sh` is called each night by cron to load data to VIVO. 
 * The `ontology` directory contains ontology extensions required for this project. 
 * The `converis` directory is a basic client for the Converis web services. This most likely will not need to be changed. 
 * The `data` directory is used to cache data needed to cache the short urls for people and organizations. This is empty. 

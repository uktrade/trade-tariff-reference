# Trade tariff reference - Deployment

The trade tariff reference is a native django application utilising the django template engine.
The application requires the following front end libraries and components:
 - node
 - npm
 - webpack
 - vue
 - babbel
 - govuk-frontend toolkit

To maintain all python packages and to keep them up to date as possible pipenv and Piplock file is
used. On starting the application locally the startup scripts will automatically try and install
the latest packages. If a new version of a package has been released it will be installed and the 
Piplock file will be updated. Its then up to the developer to test the application and if they 
are happy to then commit the updated Piplock file so the new packages will be installed in
development/staging/production environments.

 
To deploy the application in cloudfoundry two buildpacks are required.
The mainfest.yml file states both the python_buildpack and the nodejs_buildpack.

# hbp
The Higgs Boson portal

Local development server
  
    pip install pipenv
    pipenv run flask run
  

To make the main route available on the internet:

    oc annotate route <route> router.cern.ch/network-visibility=Internet

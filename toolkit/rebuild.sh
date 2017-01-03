#!/bin/bash
set -e

#
# Run the Converis to VIVO sync
# Data namespace and API credentials will be pulled from .env
#
#
cd /opt/vivo/fhutch-vivo/toolkit
source .env
source venv/bin/activate

# uri lookups
python uri_index.py 

# people and positions
python people.py
# organizations
python organizations.py
# related organizations
python related_organizations.py
# publications
python publications.py
# research areas
python areas.py
# journals
python journals.py
# news
python news.py
# awards
python awards.py
# trials
python clinical_trial.py
#data/clinicaltrials.csv
# educ 
python education_training.py
# teaching and lecture
python teaching.py
# updated photos
python pictures.py
#service
python service.py

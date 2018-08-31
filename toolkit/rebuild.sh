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

# move last harvest from current to last
mv data/current/*nt data/last/.

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
# expertise
python areas.py
# journals
python journals.py
# education and training
python education_training.py
# updated photos
python pictures.py

# sync and post additions and removals
python process_changes.py

# awards
#python awards.py
# teaching and lecture
#python teaching.py
# service
#python service.py
# news
#python news.py
# trials
#python clinical_trial.py
#data/clinicaltrials.csv

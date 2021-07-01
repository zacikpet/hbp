# HBP Server

This project contains the server-side code of the [Higgs Boson Portal](https://cern.ch/higgs).

# Developer Documentation

## Architecture

The HBP uses 3 software layers - a database, a server and a web client.

### Database

The HBP uses a [MongoDB](https://www.mongodb.com/) database. The database is hosted on the cloud by MongoDB atlas. Administration is possible via the MongoDB web interface. Contact andre.sopczak@cern.ch for more information.

### Database Collections

**papers**: collected articles

| Field | Required | Description |
| ----- | -------- | ----------- |
| _id | yes | Internal MongoDB identificator
| experiment | yes | Experiment which published this paper (atlas, cms, cdf, d0, aleph, delphi, opal, l3) |
| type | yes | **paper** or **note** |
| title | yes | Full title of the publication |
| abstract | no | Full abstract of the publication |
| date | yes | Date of publication |
| doi | no | The [Digital Object Identifier](https://www.doi.org/) |
| report_number | no | Internal CERN identificator |
| files | no | Array of links to files related to the publication |
| stage | yes | **preliminary** or **submitted** or **published** |
| superseded | no | `report_number` of the superseeding article |
| supersedes | no | `report_number` of the superseeded article |
| superseded_id | no | `_id` of the superseeding article |
| supersedes_id | no | `_id` of the superseded article |
| model | yes | **sm** (Standard Model) or **bsm** (beyond the Standard Model)
| luminosity | yes | Array of extracted luminosity values in pb<sup>-1</sup>. **Can be empty.**
| energy | yes | Array of extracted collision energies in MeV. **Can be empty.**
| production | yes | Array of extracted production modes - **ggf**, **vbf**, **whzh** or **tth**. Can be empty.
| decay | no | Object describing the decay products of the Higgs Boson | 

**users**: Administrators and users that requested an admin account

| Field | Required | Description |
| ----- | -------- | ----------- |
| _id | yes | Internal MongoDB identificator |
| email | yes | E-mail address |
| password | yes | Hashed password of the user |
| verified | yes | Whether the account has been granted admin rights: **true** or **false** |
| firstname | yes | First name |
| lastname | yes | Last name

**updates**: History of updates to the database

| Field | Required | Description |
| ----- | -------- | ----------- |
| _id | yes | Internal MongoDB identificator |
| date | yes | Date and Time when update was finished |
| trigger | no | What triggered the update: **auto** or **manual** (no value means **auto**) |

**feedbacks**: Received feedbacks from the web client

| Field | Required | Description |
| ----- | -------- | ----------- |
| _id | yes | Internal MongoDB identificator |
| date | yes | Date and time when feedback was posted |
| articles | yes | Array of related articles |
| description | yes | A description of the problem |
| comments | yes | More comments |
| email | yes | E-mail adress of the feedback sender |

### Server


Local development server
  
    pip install pipenv
    pipenv run flask run
  

To make the main route available on the internet:

    oc annotate route <route> router.cern.ch/network-visibility=Internet

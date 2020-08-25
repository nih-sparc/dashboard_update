from blackfynn.models import ModelPropertyEnumType, BaseCollection, ModelPropertyType
from blackfynn import Blackfynn, ModelProperty, LinkedModelProperty
from datetime import datetime
import blackfynn
import requests, datetime
import sys,os
import time
import json

from xml.etree import cElementTree as ElementTree

class XmlListConfig(list):
    def __init__(self, aList):
        for element in aList:
            if element:
                # treat like dict
                if len(element) == 1 or element[0].tag != element[1].tag:
                    self.append(XmlDictConfig(element))
                # treat like list
                elif element[0].tag == element[1].tag:
                    self.append(XmlListConfig(element))
            elif element.text:
                text = element.text.strip()
                if text:
                    self.append(text)

class XmlDictConfig(dict):
    '''
    Example usage:

    >>> tree = ElementTree.parse('your_file.xml')
    >>> root = tree.getroot()
    >>> xmldict = XmlDictConfig(root)

    Or, if you want to use an XML string:

    >>> root = ElementTree.XML(xml_string)
    >>> xmldict = XmlDictConfig(root)

    And then use xmldict for what it is... a dict.
    '''
    def __init__(self, parent_element):
        if parent_element.items():
            self.update(dict(parent_element.items()))
        for element in parent_element:
            if element:
                # treat like dict - we assume that if the first two tags
                # in a series are different, then they are all different.
                if len(element) == 1 or element[0].tag != element[1].tag:
                    aDict = XmlDictConfig(element)
                # treat like list - we assume that if the first two tags
                # in a series are the same, then the rest are the same.
                else:
                    # here, we put the list in dictionary; the key is the
                    # tag name the list elements all share in common, and
                    # the value is the list itself 
                    aDict = {element[0].tag: XmlListConfig(element)}
                # if the tag has attributes, add those to the dict
                if element.items():
                    aDict.update(dict(element.items()))
                self.update({element.tag: aDict})
            # this assumes that if you've got an attribute in a tag,
            # you won't be having any text. This may or may not be a 
            # good idea -- time will tell. It works for the way we are
            # currently doing XML configuration files...
            elif element.items():
                self.update({element.tag: dict(element.items())})
            # finally, if there are no child tags and no attributes, extract
            # the text
            else:
                self.update({element.tag: element.text})

def sizeof_fmt(num, suffix='B'):

    gb = 1000*1000*1000
    return float(num)/gb

def getAwardById(awards, id):
    for index, element in enumerate(awards):
        if element.values['award_id'] == id:
            return index

    return None
        
def getDatasetById(datasets, id):
    for index, element in enumerate(datasets):
        if element.values['dataset_id'] == id:
            return index
    
    return None
        
def updateValues(record, newdict):
    has_updates = False
    for key in newdict.keys():

        mapped_value = record.values[key]
        if isinstance(record.values[key], datetime.datetime):
            mapped_value = mapped_value.strftime('%Y-%m-%d')

        if not str(mapped_value) == str(newdict[key]):
            print('key: {} -- old: {} -- new: {}'.format(key, record.values[key], newdict[key]))
            record.set(key, newdict[key])
            has_updates = True
    
    if has_updates:
        print('updating')
        record.update()

def create_models(ds):
    from blackfynn import ModelProperty

    try:
        ds.get_model('SPARC_Dataset')
    except:
        dataset_schema = [
            ModelProperty('name', title=True, display_name='Name'),
            ModelProperty('owner',  data_type=str, display_name='Owner'),
            ModelProperty('owner_email', display_name='Owner email',data_type=ModelPropertyType(
                    data_type=str, format='email')),
            ModelProperty('sparc_award',  data_type=str, display_name='SPARC Award'),
            ModelProperty('award_valid',  data_type=bool, display_name='Award Valid'),
            ModelProperty('milestone_complete', data_type='date', display_name='Milestone Complete Date'),
            ModelProperty('date_created', data_type='date', display_name='Submission Date'),
            ModelProperty('first_published',  data_type='date', display_name='First published'),
            ModelProperty('status', data_type=str, display_name='Status'),
            ModelProperty('blackfynn_url',  display_name='Blackfynn URL',data_type=ModelPropertyType(
                    data_type=str, format='url')),
            ModelProperty('discover_url', display_name='Discover URL', data_type=ModelPropertyType(
                    data_type=str, format='url')),
            ModelProperty('error_index', data_type=int, display_name='Error Index'),
            ModelProperty('number_of_files',  data_type=int, display_name='Number of files'),
            ModelProperty('number_of_folders',  data_type=int, display_name='Number of folders'),
            ModelProperty('total_size', display_name='Total size',data_type=ModelPropertyType(
                    data_type=float, unit='GB' )),
            ModelProperty('doi', display_name='DOI', data_type=ModelPropertyType(
                    data_type=str, format='url')),
            ModelProperty('last_updated',  data_type='date', display_name='Last Updated'),
            ModelProperty('last_published',  data_type='date', display_name='Last published'),
            ModelProperty('status_log', display_name='Status Log', data_type=ModelPropertyEnumType(
                    data_type=str, multi_select=True)),
            ModelProperty('dataset_id',  data_type=str, display_name='Dataset ID'),
            ModelProperty('discover_id',  data_type=int, display_name='Discover ID'),
            ModelProperty('curation_priority',  data_type=str, display_name='NIH Priority')
        ]
        model = ds.create_model('SPARC_Dataset', schema = dataset_schema)

    try:
        ds.get_model('SPARC_Award')
    except:
        sparc_award_schema = [
            ModelProperty('award_id', title=True, display_name='Award ID'),
            ModelProperty('award_valid',  data_type=bool, display_name='Award Valid'),
            ModelProperty('title', display_name='Title'),
            ModelProperty('description', display_name='Description'),
            ModelProperty('principle_investigator', display_name='PI')
        ]
        award_model = ds.create_model('SPARC_Award', schema = sparc_award_schema)
    
    # try:
    #     ds.get_model('SPARC_Data_Milestone')
    # except:
    #     milestone_schema = [
    #         ModelProperty('data_description', title=True, display_name='Data Description'),
    #         ModelProperty('award', data_type=str, display_name='Status'),
    #         ModelProperty('related_milestone', data_type=int, display_name='Error Index'),
    #         ModelProperty('owner',  data_type=str, display_name='Owner'),
    #         ModelProperty('owner_email',  data_type=str, display_name='Owner email'),
    #         ModelProperty('sparc_award',  data_type=str, display_name='SPARC Award'),
    #         ModelProperty('number_of_files',  data_type=int, display_name='Number of files'),
    #         ModelProperty('total_size',  data_type=str, display_name='Total size'),
    #         ModelProperty('doi',  data_type=str, display_name='DOI'),
    #         ModelProperty('first_published',  data_type=str, display_name='First published'),
    #         ModelProperty('last_published',  data_type=str, display_name='Last published'),
    #         ModelProperty('blackfynn_id',  data_type=str, display_name='Blackfynn ID'),
    #         ModelProperty('discover_id',  data_type=int, display_name='Discover ID'),
    #         ModelProperty('blackfynn_url',  data_type=str, display_name='Blackfynn URL'),
    #         ModelProperty('discover_url',  data_type=str, display_name='Discover URL'),
    #         ModelProperty('portal_url',  data_type=str, display_name='Portal URL'),
    #         ModelProperty('curation_priority',  data_type=str, display_name='NIH Priority')
    #     ]
    #     model = ds.create_model('SPARC_Dataset', schema = dataset_schema)

    try:
        ds.get_model('Update_Run')
    except:
        process_schema = [
            ModelProperty('name', title=True, display_name='Name'),
            ModelProperty('status', data_type='date', display_name='Date'),
        ]
        award_model = ds.create_model('Update_Run', schema = process_schema)

def clearRecords(ds):
    # Clear Datasets
    model = ds.get_model('SPARC_Dataset')
    recs = model.get_all(limit=500)
    model.delete_records(*recs)

    # Clear Awards
    model = ds.get_model('SPARC_Award')
    recs = model.get_all(limit=500)
    model.delete_records(*recs)

    # Clear Milestones
    # Clear Updates
    # Not clearing because this should never be reset

def getAwardInfo(award):
    try:
        print('Getting award: {}'.format(award['award_id']))
        APIKEY = os.environ['SCICRUNCH_API_KEY']

        r = requests.get(url = u'https://scicrunch.org/api/1/dataservices/federation/data/nif-0000-10319-1?q={}&key={}'.format(award['award_id'], APIKEY))
        root = ElementTree.XML(r.content)
        resp_dict = XmlDictConfig(root)

        # Get First Result
        data = resp_dict['result']['results']['row'][0]
        mapped_data = {x['name']:x['value'] for x in data}

        award['title'] = mapped_data['Project Title']
        award['description'] = mapped_data['Abstract']
        award['principle_investigator'] = mapped_data['PI Names']
        award['award_valid'] = True

    except:
        award['award_valid'] = False 
        print('Could not get NIH Award')

def getSummary(bf):
    myDatasets = bf.datasets()
    ds_summaries = []
    i = 0

    # TEMPORARY to de-duplicate the dataset list
    myDatasets = dict((x.id,x) for x in myDatasets)
    myDatasets = list(myDatasets.values())
    # -----------------

    for ds in myDatasets:
        # Check if the dataset is shared with the curation team
        try:
            shared_with = ds.team_collaborators()
            if not any(x.name == "SPARC Data Curation Team" for x in shared_with):
                print('Skip: {}'.format(ds.name))
                continue
        except:
            print('excepted')
            continue

        print('{} : {}'.format(i,ds.name))
        i=i+1

        # if i==5:
        #     return ds_summaries

        ds_summary = {}
        ds_summary['name'] = ds.name
        ds_summary['date_created'] = datetime.datetime.strptime(ds.created_at, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d')
        ds_summary['dataset_id'] = ds.id
        ds_summary['blackfynn_url'] = u"https://app.blackfynn.io/N:organization:618e8dd9-f8d2-4dc4-9abb-c6aaab2e78a0/datasets/{}".format(ds.id)
        ds_summary['status'] = ds.status
        ds_summary['number_of_files'] = ds.package_count()
        if ds.storage:
            sz = ds.storage
        else:
            sz = 0
        
        ds_summary['total_size'] = sizeof_fmt(sz)
        ds_summary['last_updated'] = datetime.datetime.strptime(ds.updated_at, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d')
        owner = ds.owner()
        ds_summary['owner'] = owner.name 
        ds_summary['owner_email'] = owner.email 
        
        
        # Get Errors
        records = None
        try:
            summary = ds.get_model('summary')
            records = summary.get_all()

            if records:
                record = records[0]
                ds_summary['error_index'] = int(record.values['errorIndex'])
                ds_summary['number_of_folders'] = record.values['hasNumberOfDirectories']
                ds_summary['milestone_complete'] = record.values['milestoneCompletionDate'].strftime('%Y-%m-%d')

        except:
            pass    

        # Get Status_Log
        status_log = ds.status_log().entries
        str_values = []
        if status_log:
            for r in status_log:
                str_values.append('{} {} - {} - {}'.format(r.user.first_name,
                    r.user.last_name,
                    r.updated_at.strftime("%Y-%m-%d"),
                    r.status.name))

        ds_summary['status_log'] = str_values

        #Get Award
        award = None
        try:
            summary = ds.get_model('award')
            awards = summary.get_all()
            if awards:
                award = awards[0]
                ds_summary['sparc_award'] = award.values['award_id']
            else:
                ds_summary['sparc_award'] = ''

        except:
            ds_summary['sparc_award'] = ''
            pass  
  
        try:
            publish_info = ds.published()

            if publish_info.status == 'PUBLISH_SUCCEEDED':

                if publish_info.last_published:
                    ds_summary['last_published'] = datetime.datetime.strptime(publish_info.last_published, '%Y-%m-%dT%H:%M:%S.%fZ').strftime("%Y-%m-%d")

                ds_summary['discover_id'] = publish_info.dataset_id
                ds_summary['doi'] = 'https://doi.org/{}'.format(publish_info.doi)
                
                ds_summary['discover_url'] = u"https://discover.blackfynn.io/datasets/{}".format(ds_summary['discover_id'])
                
                discover_api = u"https://api.blackfynn.io/discover/datasets/{}/versions".format(ds_summary['discover_id'])
                r = requests.get(url = discover_api)
                data = r.json()
                try:
                    fp = next(iter(filter(lambda x: x["version"] == 1, data)))["createdAt"]
                    ds_summary['first_published'] = datetime.datetime.strptime(fp, '%Y-%m-%dT%H:%M:%S.%fZ').strftime("%Y-%m-%d")
                except StopIteration:
                    pass
        except:
            print('Unable to get DOI')
            # raise
            pass

    
        ds_summaries.append(ds_summary)
    
    return ds_summaries

def update(bf, ds):

    print (blackfynn.__version__)
    
    # Get current dataset summaries
    print('Getting Dataset Summaries')
    ds_summaries = getSummary(bf)

    print('Creating and Updating Dataset Records')
    # Create and update Dataset Records
    datasets = ds.get_model('SPARC_Dataset')
    datasets_recs = datasets.get_all(limit = 500)
    used_dataset_recs = set()
    for records in ds_summaries:
        record_index = getDatasetById(datasets_recs, records['dataset_id'])
        if record_index is not None:
            matched_Record = datasets_recs[record_index]
            print('{} : {}'.format(matched_Record.values['dataset_id'], records['dataset_id']))
            updateValues(matched_Record, records)
            used_dataset_recs.add(matched_Record.values['dataset_id'])
        else:
            print('No match: creating {}'.format(records['dataset_id']))
            datasets.create_record(records)
            used_dataset_recs.add(records['dataset_id'])
    
    # Remove unused dataset records
    print('Removing Unused Dataset Records')
    for record in datasets_recs:
        if record.values['dataset_id'] not in used_dataset_recs:
            print('Removing unused dataset record: ' + record.values['dataset_id'])
            record.delete()
    
    # Create and update Award records
    print('Creating and Updating Award records')
    datasets_recs = datasets.get_all(limit=500)
    awards = ds.get_model('SPARC_Award')
    award_recs = awards.get_all(limit=500)
    used_awards = set()
    i = 0
    for record in datasets_recs:

        i=i+1
        # if i==5:
        #     break 

        new_award = {}
        if record.values['sparc_award']:

            award_index = getAwardById(award_recs, record.values['sparc_award'])
            if award_index == None:
                if record.values['sparc_award']:
                    print(record.values['sparc_award'])
                    new_award['award_id'] =  record.values['sparc_award']

                    # Get info from NIH Reporter
                    getAwardInfo(new_award)
                    naw = awards.create_record(new_award)
                    award_recs.append(naw)
                    record.relate_to(naw, relationship_type='part_of')

                    record.set('award_valid', naw.values['award_valid'])
                    record.update()
            
                # Add award-id to the set of used awards
                used_awards.add(record.values['sparc_award'])
                
            else:
                print('Add Link to Award')
                naw = award_recs[award_index]   

                # Add award-id to the set of used awards
                used_awards.add(record.values['sparc_award'])

                record.relate_to(naw, relationship_type='part_of') 
                record.set('award_valid', naw.values['award_valid'])
                record.update()
    
    # Remove unused awards
    print('Removing Unused awards')
    for award in award_recs:
        if award.values['award_id'] not in used_awards:
            # Deleting unused award
            print('Removing unused award: ' + award.values['award_id'])
            award.delete()

    # Add record indicating the script ran succesfully
    now = datetime.datetime.now()
    update_run = ds.get_model('Update_Run')
    update_run.create_record({'name':'Dashboard Update','status':now})

def lambda_handler(event, context):
    DATASET = os.environ['DASHBOARD_DATASET_NAME']

    bf = Blackfynn()
    ds = bf.get_dataset(DATASET)

    update(bf, ds)

    return {
        'statusCode': 200,
        'body': json.dumps('Successfully updated the SPARC dashboard')
    }
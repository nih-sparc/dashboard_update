from blackfynn import Blackfynn
import blackfynn
import requests, datetime
import sys
import time
import json

def sizeof_fmt(num, suffix='B'):
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Y', suffix)

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
        if not str(record.values[key]) == str(newdict[key]):
            print('key: {} -- old: {} -- new: {}'.format(key, record.values[key],newdict[key]))
            record.set(key, newdict[key])
            # print('new: ' + str(record.values[key]))
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
            ModelProperty('status', data_type=str, display_name='Status'),
            ModelProperty('error_index', data_type=int, display_name='Error Index'),
            ModelProperty('owner',  data_type=str, display_name='Owner'),
            ModelProperty('owner_email',  data_type=str, display_name='Owner email'),
            ModelProperty('sparc_award',  data_type=str, display_name='SPARC Award'),
            ModelProperty('number_of_files',  data_type=int, display_name='Number of files'),
            ModelProperty('total_size',  data_type=str, display_name='Total size'),
            ModelProperty('date_created', data_type='date', display_name='Dataset Created'),
            ModelProperty('doi',  data_type=str, display_name='DOI'),
            ModelProperty('first_published',  data_type='date', display_name='First published'),
            ModelProperty('last_published',  data_type='date', display_name='Last published'),
            ModelProperty('dataset_id',  data_type=str, display_name='Dataset ID'),
            ModelProperty('discover_id',  data_type=int, display_name='Discover ID'),
            ModelProperty('blackfynn_url',  data_type=str, display_name='Blackfynn URL'),
            ModelProperty('discover_url',  data_type=str, display_name='Discover URL'),
            ModelProperty('portal_url',  data_type=str, display_name='Portal URL'),
            ModelProperty('curation_priority',  data_type=str, display_name='NIH Priority')
        ]
        model = ds.create_model('SPARC_Dataset', schema = dataset_schema)

    try:
        ds.get_model('SPARC_Award')
    except:
        sparc_award_schema = [
            ModelProperty('award_id', title=True, display_name='Award ID'),
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

def populateAwardsWithInfo(ds):
    awards = ds.get_model('SPARC_Award')
    award_recs = awards.get_all(limit=500)

    for award in award_recs:
        try:
            r = requests.get(url = u'https://api.federalreporter.nih.gov/v1/projects/search?query=projectNumber:*{}*'.format(award.values['award_id']))
            data = r.json()
            if data['totalCount'] > 0:
                data1 = data['items'][0]
                award.set('title',data1['title'])
                award.set('description',data1['abstract'])
                award.set('principle_investigator', data1['contactPi'])
                print('updating: {}'.format(award.values['award_id']))
                award.update()
        except:
            print('Could not get NIH Award')

def getSummary(bf):
    myDatasets = bf.datasets()
    ds_summaries = []
    i = 0

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

        
        
        # print("--- %s seconds ---" % (time.time() - start_time))


        print(i)
        i=i+1

        ds_summary = {}
        ds_summary['name'] = ds.name
        ds_summary['date_created'] = datetime.datetime.strptime(ds.created_at, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d 00:00:00')
        ds_summary['dataset_id'] = ds.id
        ds_summary['blackfynn_url'] = u"https://app.blackfynn.io/N:organization:618e8dd9-f8d2-4dc4-9abb-c6aaab2e78a0/datasets/{}".format(ds.id)
        ds_summary['status'] = ds.status
        ds_summary['number_of_files'] = ds.package_count()
        if ds.storage:
            sz = ds.storage
        else:
            sz = 0
        
        ds_summary['total_size'] = sizeof_fmt(sz)
    #     ds_summary['teams'] = ds.team_collaborators()
    #     ds_summary['users'] = ds.user_collaborators()
        owner = ds.owner()
        ds_summary['owner'] = owner.name 
        ds_summary['owner_email'] = owner.email 
        
        
        # Get Errors
        records = None
        try:
            # start_time = time.time()
            summary = ds.get_model('summary')
            # print("--- %s seconds  getmodel ---" % (time.time() - start_time))
            # start_time = time.time()
            records = summary.get_all()
            # print("--- %s seconds getrecord---" % (time.time() - start_time))
        except:
            pass    

        if records:
            record = records[0]
            ds_summary['error_index'] = int(record.values['errorIndex'])
        

        #Get Award
        award = None
        try:
            summary = ds.get_model('award')
            awards = summary.get_all()
        except:
            pass  

        if awards:
            award = awards[0]
            ds_summary['sparc_award'] = award.values['award_id']


        try:
            publish_info = ds.published()

            if publish_info.status == 'PUBLISH_SUCCEEDED':

                if publish_info.last_published:
                    ds_summary['last_published'] = datetime.datetime.strptime(publish_info.last_published, '%Y-%m-%dT%H:%M:%S.%fZ').strftime("%m/%d/%Y")

                ds_summary['discover_id'] = publish_info.dataset_id
                ds_summary['doi'] = publish_info.doi
                
                ds_summary['discover_url'] = u"https://discover.blackfynn.io/datasets/{}".format(ds_summary['discover_id'])
                
                discover_api = u"https://api.blackfynn.io/discover/datasets/{}/versions".format(ds_summary['discover_id'])
                ds_summary['portal_url'] = ''
                r = requests.get(url = discover_api)
                data = r.json()
                try:
                    fp = next(iter(filter(lambda x: x["version"] == 1, data)))["createdAt"]
                    ds_summary['first_published'] = datetime.datetime.strptime(fp, '%Y-%m-%dT%H:%M:%S.%fZ').strftime("%m/%d/%Y")
                except StopIteration:
                    pass
        except:
            print('Unable to get DOI')
            pass

    
        ds_summaries.append(ds_summary)
    
    return ds_summaries

def update(bf, ds):

    print (blackfynn.__version__)
    
    # Get current dataset summaries
    ds_summaries = getSummary(bf)

    # Create and update Dataset Records
    datasets = ds.get_model('SPARC_Dataset')
    datasets_recs = datasets.get_all(limit = 500)
    for records in ds_summaries:
        record_index = getDatasetById(datasets_recs, records['dataset_id'])
        if record_index is not None:
            print('Matched {}'.format(record_index))
            matched_Record = datasets_recs[record_index]
            print('{} : {}'.format(matched_Record.values['dataset_id'],records['dataset_id']))
            updateValues(matched_Record, records)
        else:
            print('No match: creating {}'.format(records['dataset_id']))
            datasets.create_record(records)
    
    # Create and update Award records
    datasets_recs = datasets.get_all(limit=500)
    awards = ds.get_model('SPARC_Award')
    award_recs = awards.get_all(limit=500)
    for record in datasets_recs:
        new_award = {}
        if record.values['sparc_award']:
            award_index = getAwardById(award_recs, record.values['sparc_award'])
            if award_index == None:
                if record.values['sparc_award']:
                    print(record.values['sparc_award'])
                    new_award['award_id'] =  record.values['sparc_award']
                    naw = awards.create_record(new_award)
                    award_recs.append(naw)
            else:
                print('update record')
                naw = award_recs[award_index]     
        
            record.relate_to(naw, relationship_type='part_of')

    # Update Award Records with info from NIH Reporter
    populateAwardsWithInfo(ds)

    # Add record indicating the script ran succesfully
    now = datetime.datetime.now()
    update_run = ds.get_model('Update_Run')
    update_run.create_record({'name':'Dashboard Update','status':now})


def lambda_handler(event, context):
    bf = Blackfynn()
    ds = bf.get_dataset('SPARC Datasets')

    update(bf, ds)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
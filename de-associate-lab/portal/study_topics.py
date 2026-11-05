"""Question-by-question study taxonomy. Topic assignments do not verify answer keys."""
TOPICS = {
 'architecture': (1,'What Databricks is',[3,4,9,15,29,47,54,69,74,91,93,95,140,203,241,251],'lab1_ingestion','1a'),
 'compute': (1,'Choose the right compute',[49,77,92,148,157,162,166,167,173,180,191,192,193,201,207,220,259,272,275],'lab7_troubleshooting','7d'),
 'notebooks': (1,'Notebooks and languages',[56,147],'lab7_troubleshooting','7d'),
 'files': (2,'Load files and database rows',[17,19,21,58,78,103,108,109,133,144,151,158,179,182,238,250,265,270],'lab1_ingestion','1c'),
 'autoloader': (2,'Auto Loader, schemas and checkpoints',[7,71,76,122,123,168,221,232,255],'lab1_ingestion','1d'),
 'connectors': (2,'Choose an ingestion connector',[227,234,247,263],'lab1_ingestion','1d'),
 'connect': (2,'Local development, remote Spark',[149,200,205,215],'lab1_ingestion','1d'),
 'medallion': (3,'Bronze, silver and gold',[26,50,65,73,81,119,124,141,152,154,159,183,202,204,213],'lab6_transform_tuning','6a'),
 'delta': (3,'Delta tables and table history',[5,6,16,20,52,59,70,98,104,219,280],'lab1_ingestion','1h'),
 'sql': (3,'Read SQL and Python step by step',[8,12,13,18,28,48,53,57,66,75,99,100,105,110,111,114,134,145,150,174,217,222],'lab5_delta_sql_streaming','5b'),
 'objects': (3,'Tables, views and materialized views',[10,24,102,245,273],'lab3_pipelines','3a'),
 'joins': (3,'Joins, unions and broadcast',[1,39,68,112,258,266,267,278],'lab6_transform_tuning','6b'),
 'nested': (3,'JSON, structs and arrays',[2,62,113,236,240],'lab1_ingestion','1g'),
 'cleaning': (3,'Nulls and duplicate records',[229,254,256,279],'lab6_transform_tuning','6c'),
 'pipelines': (3,'Declarative pipelines and quality rules',[25,32,33,34,36,42,63,72,80,116,117,120,121,126,138,146,160,225],'lab3_pipelines','3b'),
 'streaming': (3,'Streaming reads, writes and progress',[30,31,67,79,115,118,125],'lab5_delta_sql_streaming','5d'),
 'jobs': (4,'Tasks, dependencies and repair runs',[37,41,60,84,128,129,135,153,172,175,206,218,223,239,252,253,261,264,276],'lab2_jobs','2c'),
 'triggers': (4,'When should the job start?',[27,38,40,55,86,88,90,235,246,274],'lab2_jobs','2b'),
 'git': (5,'Version control and collaboration',[35,46,94,97],'lab8_cicd_bundles','8a'),
 'bundles': (5,'Deploy the same project safely',[136,137,189,190,208,214,228,242,244,249,262,271,277],'lab8_cicd_bundles','8b'),
 'diagnosis': (6,'Find the cause before changing settings',[43,82,87,127,130,131,139,164,177,178,181,185,186,224,237,243,268,269],'lab7_troubleshooting','7a'),
 'maintenance': (6,'File layout and automated maintenance',[51,101,155,170,187,188,233],'lab7_troubleshooting','7b'),
 'permissions': (7,'Who can use which data?',[11,22,44,45,61,83,85,89,96,163,176,195,197,210,226,260],'lab9_governance','9a'),
 'lifecycle': (7,'Managed and external data',[23,64,106,107,165,211,212,216,248,257],'lab9_governance','9b'),
 'sharing': (7,'Sharing, federation and lineage',[132,142,143,169,171,184,194,196,198,199,209],'lab9_governance','9a'),
 'security': (7,'Protect sensitive rows and columns',[14,156,161,230,231],'lab9_governance','9c'),
}

def topic_index():
    out = {}
    for key, (section, title, numbers, lab, gid) in TOPICS.items():
        for n in numbers:
            if n in out:
                raise ValueError(f'Question {n} assigned twice')
            out[n] = {"id":key,"section":section,"title":title,"lab":lab,"gid":gid}
    if set(out) != set(range(1,281)):
        raise ValueError(f'Topic coverage missing {sorted(set(range(1,281))-set(out))}')
    return out

def attach_learning(questions):
    from portal.exam_sections import SECTIONS
    index = topic_index()
    for q in questions:
        topic = index[q['number']]
        q.update(topic=topic['id'], section=topic['section'], legacy_section=SECTIONS[topic['section']-1]['legacy'],
                 mapping='question-by-question learning topic; suggested answer unverified')
    return questions

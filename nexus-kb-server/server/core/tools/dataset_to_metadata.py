from server.model.entity_knb import Dataset as DatasetEntity, ReposQuest as ReposQuestEntity, DatasetPrecis as DatasetPrecisEntity, DatasetTriplet as DatasetTripletEntity

def dataset_to_dict(dataset: DatasetEntity):
  return dataset.to_dict(convert=lambda key, value: '' if value is None else value, excludes=['crtUser', 'crtTm', 'idxSts', 'enbSts', '_sa_instance_state'])
# qa转为向量库元数据
def quest_to_metadata(quest: ReposQuestEntity, dataset: DatasetEntity = None):
  metadata = {
    'qstId': quest.qstId
  }
  if (dataset is not None):
    dataset = dataset_to_dict(dataset)
    metadata.update(dataset)
  return metadata

# 摘要转为向量库元数据
def precis_to_metadata(precis: DatasetPrecisEntity, dataset: DatasetEntity = None):
  metadata = {
    'prcsId': precis.prcsId
  }
  if (dataset is not None):
    dataset = dataset_to_dict(dataset)
    metadata.update(dataset)
  return metadata

def triplet_to_metadata(triplet: DatasetTripletEntity, dataset: DatasetEntity = None):
  metadata = {
    'tpltId': triplet.tpltId
  }
  if (dataset is not None):
    dataset = dataset_to_dict(dataset)
    metadata.update(dataset)
  return metadata
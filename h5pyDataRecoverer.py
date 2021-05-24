from numpy import ndarray, asarray, array, zeros, ones, newaxis
from typing import List, Dict, Tuple, Any, Generator, TypeVar
from sequenceGenerator import SequenceGenerator
from sequenceConstructor import SequenceConstructor
from imageEditor import ImageEditor
from h5py import File, Group
from timeit import timeit
class H5PYDataRetriever:
    T: TypeVar = TypeVar('T', List[Dict], List[ndarray])

    def __init__(self, fileName: str, mode: str) -> None:
        self.__file: File = File(fileName, mode)

    def getDataFile(self) -> Generator:
        groups: List[Tuple] = list(self.__file.keys())
        length: int = len(groups)
        group: Group = None;
        if(length> 0):
            try:
                for i in range(length):
                    group = self.__file.get(groups[i][0])
            except Exception as e:
                print(e)
        datasets: List[str] = list(self.__file.keys())
        print(datasets)
        data: Any = None;
        for dataset in range(len(datasets)):
            data = self.__file[datasets[dataset]][:];
            self.__file.close()
            yield asarray(data)
    @staticmethod
    def writerDataIntoH5PY( filename: str, groupname:str, datasetname: List[str], data: T) -> None:
        group: Group = None
        datasetLength: int = len(datasetname);
        dataLength: int = len(data);

        with File(filename, 'w') as file:
            group = file.create_group(groupname)
            assert(datasetLength==dataLength), 'The number of datasets and data content are not equal'
            for i in range(dataLength):
                group.create_dataset(datasetname[i], data= data[i]);



if __name__ == '__main__':
    fileName: str = 'binocular_perception.h5'
    fileName2: str = 'scene_records.h5'
    opener: H5PYDataRetriever = H5PYDataRetriever(fileName2, 'r');
    # batch ist hier die gesamte Stichprobegröße
    #gen: Generator = opener.getDataFile(fileName);
    #img: ndarray = next(gen);
    gen2: Generator = opener.getDataFile();
    scene: ndarray = array(next(gen2));
    print("SCENE SHAPE:",scene.shape);
    # ------------------------------ create a h5 file
    newname: str = 'newfile'
    groupname: str = 'cameras'
    datasets: List[str] = ['binocularCameras', 'sceneCamera']
    #data: List[ndarray] = [img, scene]
    #opener.writerDataIntoH5PY(newname, groupname, datasets, data)

    # ------------------------------ picture edition
    edition: ImageEditor = ImageEditor()
    imgList: List[ndarray] = list()
    for i in range(len(scene)):
        imgList.append(edition.editImagArray(scene[i], equa_method='clahe', scale=80))
    print(len(imgList))
    for i in range(len(imgList)//10):
        #print(edition.showImage(imgList[i], index=i))
        edition.calculateHist(imgList[i])
        print(imgList[i].shape)
    scene = array(imgList);
    # ------------------------------ sequence contruction ------------------
    dataset_size: int = 51; # Anzahl an Bilder/Frames im gesammten Datensatz
    trial_size: int = 10; # Anzahl an Frames im Trial
    trialSample_size: int = dataset_size//trial_size # Anzahl an Trials aus dem gesammten Frames-Anzahl

    start, end = 0,3 #type: int, int # BATCH SIZE
    onset: float = timeit()
    sequences: SequenceGenerator = SequenceGenerator(trialSample_size, trial_size);
    I: ndarray = sequences.samples(scene, start, end)
    offset: float = timeit()
    print(I.shape)

    print("elapsed time for sequence generator:", onset - offset)
    # ------------------------------ sequence construction

    onset2: float = timeit()
    sequencesSC: SequenceConstructor = SequenceConstructor(dataset_size, trial_size);
    SC: ndarray = sequencesSC.samples(scene, start, end);
    offset: float = timeit()
    print(SC.shape)
    offset2: float = timeit()

    print('elapsed time for sequence constructor:', onset2 - offset2);

    # ------------------------ CHANGE OF SHAPE

    newScene: ndarray = SC[..., newaxis]
    print(newScene.shape)
    print(newScene)





import pickle
from services.cluster import ClusterService
from services.database import DatabaseService
from sentence_transformers import SentenceTransformer

from modAL.models import ActiveLearner
from modAL.uncertainty import entropy_sampling

from sklearn.ensemble import RandomForestClassifier

embedder = SentenceTransformer('distiluse-base-multilingual-cased-v2')


class ClassificationService:
    @staticmethod
    def prepare():
        documents = DatabaseService.getAllUploadedDocument()
        X_train = []
        X_train_corpus = []
        for doc in documents:
            X_train_corpus.append(doc[4])
        X_train = embedder.encode(X_train_corpus)
        cluster = ClusterService(5)
        initialSample = cluster.cluster(X_train, documents)
        return initialSample

    @staticmethod
    def initial(documents):
        X_train = []
        Y_train = []
        X_train_corpus = []
        for document in documents:
            record = DatabaseService.getDoucmentByID(document['id'])
            X_train_corpus.append(record[4])
            Y_train.append(document['label'])
        X_train = embedder.encode(X_train_corpus)
        learner = ActiveLearner(
            estimator=RandomForestClassifier(n_jobs=4),
            query_strategy=entropy_sampling,
            X_training=X_train, y_training=Y_train
        )
        with open('./model/{modelName}_{i}'.format(modelName='model_', i=0), 'wb') as file:
            pickle.dump(learner, file)
        return "Success"

    @staticmethod
    def predict(id):
        corpus = []
        record = DatabaseService.getDoucmentByID(id)
        corpus.append(record[4])
        embeddings = embedder.encode(corpus)
        with open('./model/{modelName}_{i}'.format(modelName='model_', i=0), 'rb') as file:
            learner = pickle.load(file)
        prediction = learner.predict(embeddings)[0]
        label = DatabaseService.getLabelByID(prediction)
        return label

    @staticmethod
    def confirm(id, label):
        corpus = []
        record = DatabaseService.getDoucmentByID(id)
        corpus.append(record[4])
        embeddings = embedder.encode(corpus)
        with open('./model/{modelName}_{i}'.format(modelName='model_', i=0), 'rb') as file:
            learner = pickle.load(file)
        learner.teach(embeddings.reshape(1, -1), [label])
        with open('./model/{modelName}_{i}'.format(modelName='model_', i=0), 'wb') as file:
            pickle.dump(learner, file)
        DatabaseService.updateDocumentStatusAndLabbel(id, status='confirmed', label=label)
        return "Confirmed"
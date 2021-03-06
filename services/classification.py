import pickle
from database.services.Documents import DocumentsQueryService
from database.services.Labels import LabelsQueryService
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
        documents = DocumentsQueryService.getAllUploaded()
        X_train = []
        X_train_corpus = []
        for doc in documents:
            X_train_corpus.append(doc['content'])
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
            record = DocumentsQueryService.getSpecific(document['id'])
            X_train_corpus.append(record['content'])
            Y_train.append(document['label_id'])
        X_train = embedder.encode(X_train_corpus)
        learner = ActiveLearner(
            estimator=RandomForestClassifier(n_jobs=4),
            query_strategy=entropy_sampling,
            X_training=X_train, y_training=Y_train
        )
        with open('./model/model_{user_id}.pkl'.format(user_id='a305f520-2a36-4f3b-8bab-72113e04f355'), 'wb') as file:
            pickle.dump(learner, file)
        return "Success"

    @staticmethod
    def predict(id):
        corpus = []
        record = DocumentsQueryService.getSpecific(id)
        corpus.append(record['content'])
        embeddings = embedder.encode(corpus)
        with open('./model/model_{user_id}.pkl'.format(user_id='a305f520-2a36-4f3b-8bab-72113e04f355'), 'rb') as file:
            learner = pickle.load(file)
        prediction = learner.predict(embeddings)[0]
        label = LabelsQueryService.getSpecific(prediction)
        return label

    @staticmethod
    def confirm(id, label):
        corpus = []
        record = DocumentsQueryService.getSpecific(id)
        corpus.append(record['content'])
        embeddings = embedder.encode(corpus)
        with open('./model/model_{user_id}.pkl'.format(user_id='a305f520-2a36-4f3b-8bab-72113e04f355'), 'rb') as file:
            learner = pickle.load(file)
        learner.teach(embeddings.reshape(1, -1), [label])
        with open('./model/model_{user_id}.pkl'.format(user_id='a305f520-2a36-4f3b-8bab-72113e04f355'), 'wb') as file:
            pickle.dump(learner, file)
        status = DocumentsQueryService.update(
            id, {'status': 'confirmed', "label_id": label})
        return status

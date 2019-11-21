import numpy as np
from scipy import spatial
import matplotlib.pyplot as plt
import matplotlib
import cv2,  os
from math import sqrt
from database_connection import DatabaseConnection
import psycopg2
import itertools
import collections
import pprint
import os
from pathlib import Path

def get_image_directory():
    return str(Path(os.getcwd()).parent) + '/Data/images'

def get_euclidian_distance(vector1, vector2):
    return np.linalg.norm(vector1 - vector2)


def read_from_database(model,label=None):
    database_connection = DatabaseConnection()
   
    if label==None:
        img_data_matrix_dict=database_connection.get_object_feature_matrix_from_db(tablename=model)
        return img_data_matrix_dict

def get_dot_distance(vector1, vector2):
    return np.dot(vector1, vector2)


def get_cosine_similarity(vector1, vector2):
    return spatial.distance.cosine(vector1, vector2)



def plot_scree_test(eigen_values):
    num_vars = len(eigen_values)

    fig = plt.figure(figsize=(8, 5))
    sing_vals = np.arange(num_vars) + 1
    plt.plot(sing_vals, eigen_values, 'ro-', linewidth=2)
    plt.title('Scree Plot')
    plt.xlabel('K latent semantic')
    plt.ylabel('Eigenvalue')

    leg = plt.legend(['Eigenvalues from SVD'], loc='best', borderpad=0.3,
                     shadow=False, prop=matplotlib.font_manager.FontProperties(size='small'),
                     markerscale=0.4)
    leg.get_frame().set_alpha(0.4)
    plt.show()

def get_most_m_similar_images(data_with_images, query_image_feature_vector, Vt, m):
    """
    Author: Vibhu Varshney
    This funcion computes the similarity score between the query image vector and the images in the database
    :param data_with_images_: This is a dict/map with image name list and the data matrix
    :param query_image_feature_vector : Query Image feature vector after applying the feature extraction model
    :param Vt: This is the latent-vector by original feature matrix generated from either model
    :param m: Number of similar images to be returned
    :return: dictionary of m most similar images as keys and their scores as value
    """
    db_data_matrix = data_with_images.get('data_matrix')
    imageNames = data_with_images.get('images')
    database_images_latent_vectors = np.dot(db_data_matrix, np.transpose(Vt))
    query_image_latent_vector = np.dot(np.array(query_image_feature_vector),Vt.T)
    return get_top_m_tuples_by_similarity_score(database_images_latent_vectors, query_image_latent_vector, imageNames, m+1) #+1 because the db contains the query image also

def get_top_m_tuples_by_similarity_score(database_images_latent_vectors, query_image_latent_vector, imageNames, m, distance_measure = "Euclidean"):
    similar_images = get_similarity_score(database_images_latent_vectors, query_image_latent_vector, imageNames, distance_measure)
    if(distance_measure == "cosine"):
        similar_images = sorted(similar_images.items(), key=lambda k: k[1], reverse=True)
    else:
        similar_images = sorted(similar_images.items(), key=lambda k: k[1])
    top_m_tuples = similar_images[:m]
    return top_m_tuples

def get_similarity_score(database_images_latent_vectors, query_image_latent_vector, imageNames, distance_measure = "Euclidean"):
    """
    Author: Vibhu Varshney

    :param database_images_latent_vectors:
    :param query_image_latent_vector:
    :param imageNames:
    :return:
    """
    similar_images = {}
    for i in range(len(database_images_latent_vectors)):
        imageName = imageNames[i]
        db_latent_vector = database_images_latent_vectors[i]
        if(distance_measure == "Euclidean"):
            distance = get_euclidian_distance(query_image_latent_vector, db_latent_vector)
        elif(distance_measure == "dot"):
            distance = get_dot_distance(query_image_latent_vector, db_latent_vector)
        elif (distance_measure == "cosine"):
            distance = get_cosine_similarity(query_image_latent_vector, db_latent_vector)

        similar_images[imageName] = distance
    return similar_images

def get_euclidian_distance(vector1, vector2):
    return np.linalg.norm(vector1 - vector2)

def get_dot_distance(vector1, vector2):
    return np.dot(vector1, vector2)

def get_cosine_similarity(vector1, vector2):
    return spatial.distance.cosine(vector1, vector2)        
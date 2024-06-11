import cv2
from sklearn.cluster import KMeans
import logging


logger = logging.getLogger('API-offline')


def dominance_color(config: dict = None, img_path: str = "", clusters: int = 3) -> list:
    logger.info("Opening the image and convert it to RGB")
    img = cv2.imread(img_path)
    if config['color_space'] == "hsv":
        img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    if config['color_space'] == "lab":
        img = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    if config['color_space'] == "ycrcb" or config['color_space'] == "ycc":
        img = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
    if config['color_space'] == "rgb":
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    logger.info("Reshape the image as vector for the clustering algorithm")
    reshaped_img = img.reshape((img.shape[0] * img.shape[1], 3))
    logger.info("Created the clustering algorithm based on KMeans")
    if config is not None:
        kmeans_clustering = KMeans(config['n_colours'])
    else:
        kmeans_clustering = KMeans(clusters)
    logger.info("Clustering the images colour")
    kmeans_clustering.fit(reshaped_img)
    logger.info("Get the cluster centroid")
    dominance_color = kmeans_clustering.cluster_centers_
    dominance_color = dominance_color.astype(int)
    return dominance_color.tolist()

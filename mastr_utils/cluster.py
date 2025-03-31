import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from math import radians

def cluster_punkte_wolke(punkte, cluster_radius_m = 1000, min_weight = 0):
    # Umwandeln in Radian für DBSCAN (Haversine-Metrik erwartet das)
    coords = np.array([[radians(p[0]), radians(p[1])] for p in punkte.values])
    gewichte = np.array([p[2] for p in punkte])

    # Erdkugel-Radius
    earth_radius = 6371000

    # DBSCAN-Clustering (eps muss in Radiant, daher Meter / Erdradius)
    db = DBSCAN(eps=cluster_radius_m / earth_radius, min_samples=1, metric='haversine')
    labels = db.fit_predict(coords)

    # Cluster-Zentren und Summen berechnen
    cluster_resultate = []
    for cluster_id in set(labels):
        indices = np.where(labels == cluster_id)[0]
        cluster_punkte = [punkte.values[i,:] for i in indices]

        # Schwerpunkt als Durchschnitt (könnte auch der erste Punkt sein, je nach Bedarf)
        lat_mittel = np.mean([p[0] for p in cluster_punkte])
        lon_mittel = np.mean([p[1] for p in cluster_punkte])
        gewicht_summe = np.sum([p[2] for p in cluster_punkte])

        if gewicht_summe >= min_weight:
            cluster_resultate.append([float(lat_mittel), float(lon_mittel), float(gewicht_summe), int(indices[0])])

    return cluster_resultate

def filter_large_weights(data, cluster_radius_m = 1000, min_weight = 0):
    redata = data
    mydata = redata[["KoordinateLängengrad_wgs84_","KoordinateBreitengrad_wgs84_","BruttoleistungDerEinheit"]]    
    cluster_resultate = cluster_punkte_wolke(mydata, cluster_radius_m=cluster_radius_m, min_weight=min_weight)

    for i in range(len(cluster_resultate[:])):
        for j,col in enumerate(mydata.columns):
            idx = cluster_resultate[i][3]
            redata.at[redata.iloc[idx].name,col] = float(cluster_resultate[i][j])
            # print(f"idx: {idx}, col: {col}, val: {float(cluster_resultate[i][j])}")
    return redata

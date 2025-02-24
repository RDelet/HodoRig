from __future__ import annotations

import numpy as np
from scipy.optimize import minimize
from numpy.linalg import svd, norm

import maya.cmds as cmds
import maya.api.OpenMaya as om


# ----------------------------------------------------------------
# API Utils
# ----------------------------------------------------------------

_msl = om.MSelectionList()


def get_object(node: str) -> om.MObject:
    try:
        _msl.clear()
        _msl.add(node)
        return _msl.getDependNode(0)
    except RuntimeError:
        raise RuntimeError(f"Node {node} does not exist !")


def get_path(node: str | om.MObject) -> om.MDagPath:
    if isinstance(node, om.MObject):
        if not node.hasFn(om.MFn.kDagNode):
            raise RuntimeError(f"Node {om.MFnDependencyNode(node).name()} is not a dagNode !")
        return om.MDagPath.getAPathTo(node)
    try:
        _msl.clear()
        _msl.add(node)
        return _msl.getDagPath(0)
    except RuntimeError:
        raise RuntimeError(f"Node {node} does not exist !")


def name(obj: str | om.MObject | om.MPlug, full: bool = True, namespace: bool = True) -> str:
    if isinstance(obj, om.MDagPath):
        name_str = obj.fullPathName()
    elif isinstance(obj, om.MPlug):
        node_name = name(obj.node())
        attr_name = om.MFnAttribute(obj.attribute()).name()
        name_str = f"{node_name}.{attr_name}"
    elif isinstance(obj, om.MObject):
        if not obj.hasFn(om.MFn.kDagNode):
            name_str = om.MFnDependencyNode(obj).name()
        else:
            name_str = om.MFnDagNode(obj).fullPathName()
    else:
        raise TypeError(f"Argument must be a MObject not {type(obj)}")
    if not full:
        name_str = name_str.split('|')[-1]
    if not namespace:
        name_str = name_str.split(':')[-1]
    return name_str


def get_points(obj: str | om.MDagPath | om.MObject):
    if not isinstance(obj, om.MDagPath):
        obj = get_path(obj)
    mfn = om.MFnMesh(obj)
    points = mfn.getPoints(om.MSpace.kObject)
    return points


def simple_kmeans(X, n_clusters, n_iter=100):
    """
    Implémentation simple du K-means avec NumPy.
    Paramètres:
        X : ndarray, shape (N, d)
            Données à regrouper.
        n_clusters : int
            Nombre de clusters.
        n_iter : int
            Nombre maximum d'itérations.
    Renvoie:
        labels : ndarray, shape (N,)
            Les indices de cluster pour chaque point.
    """
    N, d = X.shape
    # Initialisation : choisir n_clusters points aléatoirement dans X
    indices = np.random.choice(N, n_clusters, replace=False)
    centers = X[indices]
    
    for it in range(n_iter):
        # Calcul des distances (N x n_clusters)
        distances = np.linalg.norm(X[:, None] - centers[None, :], axis=2)
        labels = np.argmin(distances, axis=1)
        new_centers = np.zeros_like(centers)
        for j in range(n_clusters):
            pts = X[labels == j]
            if pts.shape[0] > 0:
                new_centers[j] = pts.mean(axis=0)
            else:
                new_centers[j] = centers[j]
        if np.allclose(centers, new_centers, atol=1e-6):
            break
        centers = new_centers
    return labels


# ----------------------------------------------------------------
# API Utils
# ----------------------------------------------------------------

class SSDR:

    def __init__(self, P, V_list, num_bones, K, max_iter=50, tol=1e-4, reinit_threshold=1e-6):
        """
        Initialisation du modèle SSDR.
        
        Parameters:
            P : ndarray, shape (V, 3)
                Pose de repos (rest pose)
            V_list : list of ndarray, each shape (V, 3)
                Liste des poses exemples (T poses)
            num_bones : int
                Nombre d'os (|B|)
            K : int
                Nombre maximum d'os influents par vertex (ex. 4)
            max_iter : int
                Nombre maximum d'itérations de la descente par blocs
            tol : float
                Tolérance de convergence (relative sur l'erreur)
            reinit_threshold : float
                Seuil pour considérer qu'un os est insignifiant (pour réinitialisation)
        """
        self.P = P                          # Rest pose (V x 3)
        self.V_list = V_list                # Liste des T poses exemples (chacune V x 3)
        self.T = len(V_list)                # Nombre de poses exemples
        self.V_count = P.shape[0]           # Nombre de vertices
        self.num_bones = num_bones          # Nombre d'os
        self.K = K                          # Contrainte de sparsité (max non-zéros par vertex)
        self.max_iter = max_iter
        self.tol = tol
        self.reinit_threshold = reinit_threshold
        
        # Initialisation de la matrice de poids W (V x num_bones)
        self.W = np.zeros((self.V_count, self.num_bones))
        # Initialisation des transformations des os pour chaque pose:
        # Pour chaque pose t et chaque os j, self.R[t,j] est une rotation (3x3)
        # et self.Tt[t,j] une translation (3,)
        self.R = np.zeros((self.T, self.num_bones, 3, 3))
        self.Tt = np.zeros((self.T, self.num_bones, 3))
        
        self.initialize_bones()
        
    def initialize_bones(self):
        """
        Initialisation des poids et des transformations des os.
        On commence par assigner chaque vertex à un os via K-means (initialisation simple),
        puis on calcule, pour chaque pose, la transformation rigide par l'algorithme de Kabsch.
        """
        # Clustering initial des vertices en num_bones groupes avec simple_kmeans
        labels = simple_kmeans(self.P, self.num_bones, n_iter=100)
        
        # Initialisation des poids : chaque vertex est entièrement influencé par l'os du cluster associé
        for i in range(self.V_count):
            self.W[i, labels[i]] = 1.0
        
        # Initialisation des transformations os pour chaque pose par Kabsch sur chaque cluster
        for t in range(self.T):
            for j in range(self.num_bones):
                indices = np.where(labels == j)[0]
                if len(indices) < 3:
                    # Si le cluster est trop petit, on utilise l'identité
                    self.R[t, j] = np.eye(3)
                    self.Tt[t, j] = np.zeros(3)
                    continue
                P_subset = self.P[indices]
                V_subset = self.V_list[t][indices]
                R_opt, T_opt = self.kabsch(P_subset, V_subset)
                self.R[t, j] = R_opt
                self.Tt[t, j] = T_opt

    def kabsch(self, P, Q):
        """
        Algorithme de Kabsch pour trouver la rotation R et la translation T
        qui alignent P vers Q (P et Q de taille N x 3).
        """
        p_centroid = P.mean(axis=0)
        q_centroid = Q.mean(axis=0)
        P_centered = P - p_centroid
        Q_centered = Q - q_centroid
        C = P_centered.T @ Q_centered
        U, _, Vt = svd(C)
        R = Vt.T @ U.T
        if np.linalg.det(R) < 0:
            Vt[-1, :] *= -1
            R = Vt.T @ U.T
        T = q_centroid - R @ p_centroid
        return R, T

    def update_weights(self):
        """
        Mise à jour de la carte d'influences W.
        Pour chaque vertex i, on résout le problème de moindres carrés sous contraintes :
          min_{w} || A_i * w - b_i ||^2
          avec w >= 0, sum(w) = 1.
        A_i et b_i concatènent, pour chaque pose, la transformation (R et Tt) appliquée à P[i]
        et la position observée dans la pose exemple.
        Puis on impose la contrainte de sparsité en ne gardant que les K plus grandes valeurs.
        """
        for i in range(self.V_count):
            B = self.num_bones
            T = self.T
            A = np.zeros((3 * T, B))
            b = np.zeros(3 * T)
            for t in range(T):
                for j in range(B):
                    transformed = self.R[t, j] @ self.P[i] + self.Tt[t, j]
                    A[3*t:3*t+3, j] = transformed
                b[3*t:3*t+3] = self.V_list[t][i]
            def obj(w):
                return norm(A.dot(w) - b)**2
            cons = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
            bounds = [(0, 1) for _ in range(B)]
            w0 = np.ones(B) / B
            res = minimize(obj, w0, method='SLSQP', bounds=bounds, constraints=cons)
            w_sol = res.x
            if self.K < B:
                idx = np.argsort(w_sol)[::-1]
                mask = np.zeros(B, dtype=bool)
                mask[idx[:self.K]] = True
                w_sol[~mask] = 0
                s = np.sum(w_sol)
                if s > 1e-8:
                    w_sol /= s
            self.W[i] = w_sol

    def update_bones(self):
        """
        Mise à jour des transformations des os pour chaque pose.
        Pour chaque pose t et chaque os j, on résout le problème de Weighted Absolute Orientation :
          min_{R, T} sum_{i} w[i,j] * || V_list[t][i] - (R @ P[i] + T) ||^2
        La solution est obtenue en calculant d'abord les centroïdes pondérés, puis
        en effectuant une décomposition SVD sur la matrice de covariance pondérée.
        Si la somme des poids est trop faible, on considère l'os comme insignifiant et on le réinitialise.
        """
        T = self.T
        B = self.num_bones
        for t in range(T):
            for j in range(B):
                w = self.W[:, j]
                if np.sum(w**2) < self.reinit_threshold:
                    self.reinitialize_bone(t, j)
                    continue
                w_sum = np.sum(w)
                p_centroid = np.sum(w[:, None] * self.P, axis=0) / w_sum
                v_centroid = np.sum(w[:, None] * self.V_list[t], axis=0) / w_sum
                P_centered = self.P - p_centroid
                V_centered = self.V_list[t] - v_centroid
                C = (w[:, None] * P_centered).T @ V_centered
                U, S, Vt = svd(C)
                R_opt = Vt.T @ U.T
                if np.linalg.det(R_opt) < 0:
                    Vt[-1, :] *= -1
                    R_opt = Vt.T @ U.T
                T_opt = v_centroid - R_opt @ p_centroid
                self.R[t, j] = R_opt
                self.Tt[t, j] = T_opt

    def reinitialize_bone(self, t, j, neighbor_count=20):
        """
        Réinitialise la transformation de l'os j pour la pose t si cet os est insignifiant.
        Ici, la réinitialisation consiste simplement à réaffecter une transformation identité.
        (Une implémentation plus complète rechercherait le vertex avec la plus grande erreur
         et réinitialiserait l'os à partir de ses voisins en appliquant Kabsch.)
        """
        print(f"Réinitialisation de l'os {j} pour la pose {t} (influence trop faible).")
        self.R[t, j] = np.eye(3)
        self.Tt[t, j] = np.zeros(3)
        
    def correct_rest_pose(self):
        """
        Correction de la pose de repos P par une méthode des moindres carrés afin de réduire
        la déviation globale entre les poses reconstruites et les poses exemples.
        Ici, on résout : min_P sum_{t} || V_list[t] - sum_{j} W[i,j]*(R[t,j]*P + Tt[t,j]) ||^2
        et met à jour P. Pour simplifier, cette étape est ici laissée comme une fonction factice.
        """
        # Exemple : corriger P en moyennant les prédictions sur toutes les poses
        pass

    def compute_error(self):
        """
        Calcule l'erreur totale de reconstruction :
          E = sum_{t,i} || V_list[t][i] - sum_{j} W[i,j]*(R[t,j]*P[i] + Tt[t,j]) ||^2
        """
        err = 0.0
        T = self.T
        B = self.num_bones
        for t in range(T):
            for i in range(self.V_count):
                pred = np.zeros(3)
                for j in range(B):
                    pred += self.W[i, j] * (self.R[t, j] @ self.P[i] + self.Tt[t, j])
                err += norm(self.V_list[t][i] - pred)**2
        return err

    def run(self):
        """
        Exécute l'algorithme SSDR complet par descente par blocs jusqu'à convergence
        ou jusqu'au nombre maximum d'itérations. À chaque itération, on met à jour
        d'abord la carte d'influences, puis les transformations des os, et on surveille
        l'erreur de reconstruction.
        """
        prev_err = np.inf
        for it in range(self.max_iter):
            print(f"Itération {it}...")
            self.update_weights()
            self.update_bones()
            err = self.compute_error()
            print(f"Erreur de reconstruction : {err:.6f}")
            if abs(prev_err - err) / (prev_err + 1e-8) < self.tol:
                print("Convergence atteinte.")
                break
            prev_err = err
        self.correct_rest_pose()
        print("Algorithme terminé.")


# ----------------------------------------------------------------
# Exemple d'utilisation
# ----------------------------------------------------------------

src_mesh = "outputCloth1"
dst_mesh = "dst_planeShape"
rest_points = np.array(om.MVectorArray(get_points(dst_mesh)))

min_time = 0
max_time = 100
pose_number = max_time - min_time
joint_number = 20
max_influences = 3
# Get Pose
poses = []
cmds.refresh(suspend=True)
current_time = cmds.currentTime(query=True)
try:    
    for t in range(0, pose_number):
        cmds.currentTime(t)
        poses.append(om.MVectorArray(get_points(src_mesh)))
finally:
    cmds.currentTime(current_time)
    cmds.refresh(suspend=False)
poses = np.array(poses)
# Init SSDR
ssd = SSDR(rest_points, poses, num_bones=joint_number, K=max_influences, max_iter=30, tol=1e-4)
ssd.run()


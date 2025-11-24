# Farahzad_Morphology_Analysis
## Project Overview
This project applies **Geospatial Data Science** and **Unsupervised Machine Learning (K-Means Clustering)** to analyze and classify the urban fabric (Morphology) of the Farahzad neighborhood in Tehran. The goal is to identify distinct, hidden spatial patterns and morphological typologies based on quantifiable geometric parameters.

## Methodology & Tools
The analysis pipeline was developed entirely in **Python** using the following core libraries:
* **GeoPandas:** For handling, manipulation, and spatial operations on parcel data (GeoPackage format).
* **Scikit-learn:** For implementing the **K-Means clustering algorithm** to segment the urban tissue.
* **NumPy/Pandas:** For metric calculation and data management.
* **Matplotlib:** For producing high-quality spatial visualizations (Cluster Maps, Rose Diagrams).

## Key Calculated Metrics
The clustering was performed on four primary, normalized morphological indicators:
1.  **Area (Log-transformed):** Parcel size.
2.  **Perimeter/Area Ratio:** An inverse measure of compactness.
3.  **Rectangular Fit:** How closely a parcel matches a perfect rectangle.
4.  **Orientation:** The primary alignment of the parcel relative to North.

## Key Findings: Four Urban Typologies
The K-Means model successfully identified **four distinct morphological clusters**, each representing a unique historical development or planning era within the neighborhood:

| Cluster ID | Type Name | Avg. Area (m²) | Avg. Compactness | Avg. Rectangular Fit | Dominant Orientation | Description |
| **Cluster 0** | **Large, Irregular & Organic** | 8,376 | Low | Low | Variable | Represents large, historical land holdings, often undeveloped or topographically constrained. |
| **Cluster 1** | **Medium-sized Organic** | 620 | Medium | Medium | Dominantly North-South | Found in the older, naturally developed sections of the neighborhood. |
| **Cluster 2** | **Fine-Grained Planned** | 205 | High | High | Strict North-South / East-West | Characterizes highly dense, regularly planned residential blocks with small parcel sizes. |
| **Cluster 3** | **Small & Highly Compact** | 150 | Highest | High | Mostly East-West | Represents highly fragmented, newly developed residential areas. |

## Visual Outcomes
The results are presented through specialized maps and diagrams:

* **Cluster Map:**  A primary thematic map illustrating the spatial distribution of the **four morphological typologies** identified by the K-Means algorithm, demonstrating the spatial coherence of each urban fabric type.
* **Parcel Density Map:**  A heatmap generated via **Fishnet analysis** (50m grid) that quantifies the spatial intensity and **Urban Texture** by mapping the concentration of parcel counts per grid cell.
* **Rose Diagrams (Orientation):**  **Polar bar charts** used to visualize the dominant angular alignment of parcels for each cluster, revealing stark differences between the planned (bi-directional) and organic (chaotic) fabrics.
* **Area Distribution Map:**  A thematic map illustrating the spatial distribution of **Parcel Grain Size**, which is essential for distinguishing between large, historical plots and areas of dense, fine-grained subdivision.
* **Compactness Map:**  A thematic map that shows the **Geometric Regularity** of parcels, highlighting the transition from highly irregular (low compactness) to standardized, rectangular forms (high compactness).
* **Descriptive Cluster Table:** A key document that quantitatively summarizes the **mean values** of all calculated metrics for each morphological cluster, validating the separation achieved by the clustering model.

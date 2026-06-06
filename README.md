# 💊 PharmaSales Intelligence Data Pipeline

A full-stack, production-grade data engineering pipeline and interactive analytics dashboard built to process and visualize commercial pharmaceutical data.

**🔗 [Live Dashboard](https://procdna-pharma-pipeline.onrender.com/)** ## 🏗️ System Architecture

This project simulates a modern enterprise data stack, moving raw commercial data through an ETL pipeline into a cloud data warehouse, and finally surfacing it in a real-time BI layer.

1. **The Source:** Programmatically generated mock pharmaceutical datasets (`pandas`, `numpy`) simulating unstructured transaction logs.
2. **The Pipeline (ETL):** A Python-based extraction and transformation engine (`SQLAlchemy`) that cleans null values, enforces data typing, and calculates key business metrics (Total Revenue).
3. **The Data Warehouse:** A fully remote, cloud-hosted **PostgreSQL** relational database deployed on Render.
4. **The Presentation Layer:** An interactive, responsive Business Intelligence dashboard built with **Streamlit** and **Plotly**, featuring real-time SQL querying and dynamic cross-filtering.

## 🛠️ Technology Stack

* **Language:** Python 3.11
* **Database:** PostgreSQL (Cloud-hosted via Render)
* **Data Processing:** Pandas, NumPy
* **Database ORM:** SQLAlchemy, psycopg2
* **Frontend Analytics:** Streamlit
* **Data Visualization:** Plotly Express
* **DevOps/Deployment:** Docker, Git, Render Web Services

## 🚀 Local Development (Docker)

To run this pipeline locally in an isolated container environment:

1. Clone the repository:
   ```bash
   git clone [https://github.com/YOUR_USERNAME/procdna-pharma-pipeline.git](https://github.com/YOUR_USERNAME/procdna-pharma-pipeline.git)
   cd procdna-pharma-pipeline
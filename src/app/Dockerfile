FROM python:slim
USER root
EXPOSE 8501 1433
RUN pip install --no-cache-dir streamlit matplotlib pandas
WORKDIR /code
COPY . /code
CMD streamlit run velib.py
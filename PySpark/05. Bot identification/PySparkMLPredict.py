import argparse
from pyspark.sql import DataFrame
from pyspark.ml import PipelineModel
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler, StringIndexer
from pyspark.ml.evaluation import MulticlassClassificationEvaluator

MODEL_PATH = 'spark_ml_model'
def vector_assembler() -> VectorAssembler:
    #input_cols = [col for col in train_df.columns if col != 'is_credit_closed']
    assembler = VectorAssembler(inputCols=['user_type_index', 'duration', 'platform_index', 'item_info_events',
                                           'select_item_events', 'make_order_events', 'events_per_min'], outputCol="features")
    return assembler

def prepare_data(df: DataFrame, assembler) -> DataFrame:
    user_type_index = StringIndexer(inputCol='user_type', outputCol="user_type_index")
    platform_index = StringIndexer(inputCol='platform', outputCol="platform_index")
    df = user_type_index.fit(df).transform(df)
    df = platform_index.fit(df).transform(df)
    df = assembler.transform(df)
    return df



def main(data_path, model_path, result_path):
    """
    Применение сохраненной модели.

    :param data_path: путь к файлу с данными к которым нужно сделать предсказание.
    :param model_path: путь к сохраненой модели (Из задачи PySparkMLFit.py).
    :param result_path: путь куда нужно сохранить результаты предсказаний ([session_id, prediction]).
    """
    spark = _spark_session()
    df = spark.read.parquet(data_path)
    assembler = vector_assembler()
    df_pr = prepare_data(df, assembler)
    model = PipelineModel.load(model_path)
    predictions = model.transform(df_pr)
    result_df = predictions.select("session_id", "prediction")
    result_df.write.parquet(result_path)
    return


def _spark_session():
    """
    Создание SparkSession.

    :return: SparkSession
    """
    return SparkSession.builder.appName('PySparkMLPredict').getOrCreate()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_path', type=str, default=MODEL_PATH, help='Please set model path.')
    parser.add_argument('--data_path', type=str, default='test.parquet', help='Please set datasets path.')
    parser.add_argument('--result_path', type=str, default='result', help='Please set result path.')
    args = parser.parse_args()
    data_path = args.data_path
    model_path = args.model_path
    result_path = args.result_path
    main(data_path, model_path, result_path)
